from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import Review
from .forms import ReviewForm
from books.models import Book

try:
    from activitylog.utils import log_activity
except Exception:
    def log_activity(*args, **kwargs):
        pass


# ─────────────────────────────────────────
# ADD / EDIT REVIEW
# ─────────────────────────────────────────
@login_required
def add_review(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    # Check if user already reviewed this book
    existing = Review.objects.filter(user=request.user, book=book).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            action = 'updated' if existing else 'added'
            log_activity(request.user, 'review', f'{action.capitalize()} review for "{book.title}"')
            messages.success(request, f'Your review has been {action} successfully!')
            return redirect('books:book_detail', pk=book_id)
    else:
        form = ReviewForm(instance=existing)

    return render(request, 'reviews/add_review.html', {
        'form': form,
        'book': book,
        'existing': existing,
    })


# ─────────────────────────────────────────
# DELETE REVIEW
# ─────────────────────────────────────────
@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)

    # Only owner or admin can delete
    if review.user != request.user and not request.user.is_admin_user:
        messages.error(request, 'You do not have permission to delete this review.')
        return redirect('books:book_detail', pk=review.book.pk)

    book_id = review.book.pk
    book_title = review.book.title
    review.delete()
    log_activity(request.user, 'review', f'Deleted review for "{book_title}"')
    messages.success(request, 'Review deleted successfully.')
    return redirect('books:book_detail', pk=book_id)


# ─────────────────────────────────────────
# ALL REVIEWS FOR A BOOK
# ─────────────────────────────────────────
def book_reviews(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    reviews = Review.objects.filter(book=book).select_related('user')
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    return render(request, 'reviews/book_reviews.html', {
        'book': book,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'user_review': user_review,
        'rating_range': range(1, 6),
    })