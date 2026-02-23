from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Reservation
from books.models import Book

try:
    from activitylog.utils import log_activity
except ImportError:
    def log_activity(*args, **kwargs):
        pass


# ─────────────────────────────────────────
# RESERVATION LIST
# ─────────────────────────────────────────
@login_required
def reservation_list(request):
    if request.user.is_admin_user or request.user.is_librarian_user:
        reservations = Reservation.objects.select_related('user', 'book').all()
    else:
        reservations = Reservation.objects.select_related('user', 'book').filter(user=request.user)

    # Auto-expire old ones
    for r in reservations:
        if r.is_expired():
            r.status = 'expired'
            r.save()

    status_filter = request.GET.get('status', '')
    if status_filter:
        reservations = reservations.filter(status=status_filter)

    return render(request, 'reservation/reservation_list.html', {
        'reservations': reservations,
        'status_filter': status_filter,
    })


# ─────────────────────────────────────────
# RESERVE A BOOK
# ─────────────────────────────────────────
@login_required
def reserve_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    # Check if already reserved
    active_statuses = ['pending', 'ready']
    already_reserved = Reservation.objects.filter(
        user=request.user, book=book, status__in=active_statuses
    ).exists()

    if already_reserved:
        messages.warning(request, f'You already have an active reservation for "{book.title}".')
        return redirect('books:book_detail', pk=book_id)

    if book.available_copies > 0:
        messages.info(request, f'"{book.title}" is currently available! Please borrow it directly.')
        return redirect('books:book_detail', pk=book_id)

    if request.method == 'POST':
        reservation = Reservation.objects.create(user=request.user, book=book)
        log_activity(request.user, 'reservation', f'Reserved "{book.title}"')
        messages.success(request, f'"{book.title}" reserved successfully! We will notify you when it\'s available.')
        return redirect('reservation:reservation_list')

    return render(request, 'reservation/reserve_confirm.html', {'book': book})


# ─────────────────────────────────────────
# CANCEL RESERVATION
# ─────────────────────────────────────────
@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)

    # Only owner or admin/librarian can cancel
    if reservation.user != request.user:
        if not (request.user.is_admin_user or request.user.is_librarian_user):
            messages.error(request, 'You do not have permission to cancel this reservation.')
            return redirect('reservation:reservation_list')

    if reservation.status in ('fulfilled', 'cancelled', 'expired'):
        messages.warning(request, 'This reservation cannot be cancelled.')
        return redirect('reservation:reservation_list')

    reservation.cancel()
    log_activity(request.user, 'reservation', f'Cancelled reservation for "{reservation.book.title}"')
    messages.success(request, 'Reservation cancelled successfully.')
    return redirect('reservation:reservation_list')


# ─────────────────────────────────────────
# MARK READY (Admin/Librarian only)
# ─────────────────────────────────────────
@login_required
def mark_ready(request, pk):
    if not (request.user.is_admin_user or request.user.is_librarian_user):
        messages.error(request, 'Permission denied.')
        return redirect('reservation:reservation_list')

    reservation = get_object_or_404(Reservation, pk=pk)
    reservation.mark_ready()
    log_activity(request.user, 'reservation', f'Marked "{reservation.book.title}" ready for {reservation.user.get_full_name()}')
    messages.success(request, f'Reservation marked as Ready for Pickup. Student has 3 days to collect.')
    return redirect('reservation:reservation_list')


# ─────────────────────────────────────────
# FULFILL RESERVATION (Admin/Librarian only)
# ─────────────────────────────────────────
@login_required
def fulfill_reservation(request, pk):
    if not (request.user.is_admin_user or request.user.is_librarian_user):
        messages.error(request, 'Permission denied.')
        return redirect('reservation:reservation_list')

    reservation = get_object_or_404(Reservation, pk=pk)
    reservation.status = 'fulfilled'
    reservation.save()
    log_activity(request.user, 'reservation', f'Fulfilled reservation for "{reservation.book.title}" — issued to {reservation.user.get_full_name()}')
    messages.success(request, f'Reservation fulfilled! Now issue the book via the Issue Book page.')
    return redirect('reservation:reservation_list')