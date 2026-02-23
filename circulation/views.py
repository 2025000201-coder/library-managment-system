from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
from .models import IssuedBook, Fine, FineSettings
from .forms import IssueBookForm
from books.models import Book
from accounts.models import User


def log(user, action, desc, request=None):
    try:
        from activitylog.utils import log_activity
        log_activity(user, action, desc, request)
    except Exception:
        pass


def get_fine_per_day():
    settings = FineSettings.objects.first()
    return settings.fine_per_day if settings else Decimal('2.00')


@login_required
def issue_book(request):
    if not (request.user.is_admin_user or request.user.is_librarian_user):
        messages.error(request, "You don't have permission to issue books.")
        return redirect('dashboard:home')

    form = IssueBookForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        book = form.cleaned_data['book']
        student = form.cleaned_data['student']

        already_issued = IssuedBook.objects.filter(
            student=student, book=book, status__in=['issued', 'overdue']
        ).exists()
        if already_issued:
            messages.error(request, f"{student.get_full_name()} already has '{book.title}' issued.")
            return render(request, 'circulation/issue_book.html', {'form': form})

        if book.available_copies <= 0:
            messages.error(request, f"'{book.title}' has no available copies.")
            return render(request, 'circulation/issue_book.html', {'form': form})

        issued = form.save(commit=False)
        issued.issued_by = request.user
        issued.save()

        book.available_copies -= 1
        book.save()

        log(request.user, 'book_issued',
            f'Issued "{book.title}" to {student.get_full_name()} (Due: {issued.due_date})', request)

        messages.success(request, f"'{book.title}' issued to {student.get_full_name()} successfully!")
        return redirect('circulation:issued_list')

    return render(request, 'circulation/issue_book.html', {'form': form})


@login_required
def issued_list(request):
    queryset = IssuedBook.objects.select_related('student', 'book', 'issued_by').all()

    today = timezone.now().date()
    queryset.filter(status='issued', due_date__lt=today).update(status='overdue')

    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')

    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if search:
        queryset = queryset.filter(
            Q(student__first_name__icontains=search) |
            Q(student__last_name__icontains=search) |
            Q(student__username__icontains=search) |
            Q(book__title__icontains=search) |
            Q(book__book_id__icontains=search)
        )

    context = {
        'issued_books': queryset,
        'status_filter': status_filter,
        'search': search,
        'today': today,
    }
    return render(request, 'circulation/issued_list.html', context)


@login_required
def return_book(request, pk):
    if not (request.user.is_admin_user or request.user.is_librarian_user):
        messages.error(request, "You don't have permission to return books.")
        return redirect('dashboard:home')

    issued = get_object_or_404(IssuedBook, pk=pk)
    if issued.status == 'returned':
        messages.warning(request, "This book has already been returned.")
        return redirect('circulation:issued_list')

    today = timezone.now().date()
    fine_per_day = get_fine_per_day()
    overdue_days = max(0, (today - issued.due_date).days)
    calculated_fine = Decimal(overdue_days) * fine_per_day

    if request.method == 'POST':
        issued.return_date = today
        issued.status = 'returned'
        issued.save()

        issued.book.available_copies += 1
        issued.book.save()

        if overdue_days > 0:
            Fine.objects.create(
                issued_book=issued,
                student=issued.student,
                amount=calculated_fine,
                overdue_days=overdue_days,
                fine_per_day=fine_per_day,
                status='unpaid'
            )
            log(request.user, 'book_returned',
                f'Returned "{issued.book.title}" from {issued.student.get_full_name()} — Fine: ₹{calculated_fine}', request)
            messages.warning(request, f"Book returned! Fine of ₹{calculated_fine} applied for {overdue_days} overdue days.")
        else:
            log(request.user, 'book_returned',
                f'Returned "{issued.book.title}" from {issued.student.get_full_name()} — No fine', request)
            messages.success(request, f"'{issued.book.title}' returned successfully!")

        return redirect('circulation:issued_list')

    context = {
        'issued': issued,
        'today': today,
        'overdue_days': overdue_days,
        'fine_per_day': fine_per_day,
        'calculated_fine': calculated_fine,
    }
    return render(request, 'circulation/return_book.html', context)


@login_required
def issued_book_detail(request, pk):
    issued = get_object_or_404(IssuedBook, pk=pk)
    fine = Fine.objects.filter(issued_book=issued).first()
    return render(request, 'circulation/issued_book_detail.html', {'issued': issued, 'fine': fine})


@login_required
def fine_list(request):
    fines = Fine.objects.select_related('student', 'issued_book__book').all()

    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')

    if status_filter:
        fines = fines.filter(status=status_filter)
    if search:
        fines = fines.filter(
            Q(student__first_name__icontains=search) |
            Q(student__last_name__icontains=search) |
            Q(issued_book__book__title__icontains=search)
        )

    total_unpaid = sum(f.amount for f in fines.filter(status='unpaid'))
    total_collected = sum(f.amount for f in fines.filter(status='paid'))

    context = {
        'fines': fines,
        'status_filter': status_filter,
        'search': search,
        'total_unpaid': total_unpaid,
        'total_collected': total_collected,
    }
    return render(request, 'circulation/fine_list.html', context)


@login_required
def mark_fine_paid(request, pk):
    if not (request.user.is_admin_user or request.user.is_librarian_user):
        messages.error(request, "Permission denied.")
        return redirect('circulation:fine_list')

    fine = get_object_or_404(Fine, pk=pk)
    fine.status = 'paid'
    fine.paid_at = timezone.now()
    fine.paid_by = request.user
    fine.save()

    log(request.user, 'fine_paid',
        f'Marked fine of ₹{fine.amount} as paid for {fine.student.get_full_name()}', request)
    messages.success(request, f"Fine of ₹{fine.amount} marked as paid for {fine.student.get_full_name()}.")
    return redirect('circulation:fine_list')


@login_required
def waive_fine(request, pk):
    if not request.user.is_admin_user:
        messages.error(request, "Only admin can waive fines.")
        return redirect('circulation:fine_list')

    fine = get_object_or_404(Fine, pk=pk)
    fine.status = 'waived'
    fine.paid_by = request.user
    fine.paid_at = timezone.now()
    fine.save()

    log(request.user, 'fine_waived',
        f'Waived fine of ₹{fine.amount} for {fine.student.get_full_name()}', request)
    messages.success(request, f"Fine waived for {fine.student.get_full_name()}.")
    return redirect('circulation:fine_list')


@login_required
def my_books(request):
    issued_books = IssuedBook.objects.filter(student=request.user).select_related('book')
    fines = Fine.objects.filter(student=request.user, status='unpaid')
    context = {
        'issued_books': issued_books,
        'fines': fines,
        'today': timezone.now().date(),
    }
    return render(request, 'circulation/my_books.html', context)