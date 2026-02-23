from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Book, Category, Publisher
from .forms import BookForm, CategoryForm, PublisherForm


# ─────────────────────────────────────────
# BOOK LIST + SEARCH + FILTER
# ─────────────────────────────────────────
@login_required
def book_list(request):
    books = Book.objects.select_related('category', 'publisher').all()
    categories = Category.objects.all()

    # Search
    query = request.GET.get('q', '')
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query) |
            Q(book_id__icontains=query)
        )

    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        books = books.filter(category__id=category_id)

    # Filter by availability
    availability = request.GET.get('availability', '')
    if availability == 'available':
        books = books.filter(available_copies__gt=0)
    elif availability == 'unavailable':
        books = books.filter(available_copies=0)

    return render(request, 'books/book_list.html', {
        'books': books,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'selected_availability': availability,
    })


# ─────────────────────────────────────────
# BOOK DETAIL
# ─────────────────────────────────────────
@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/book_detail.html', {'book': book})


# ─────────────────────────────────────────
# ADD BOOK
# ─────────────────────────────────────────
@login_required
def book_add(request):
    if not (request.user.is_admin_user or request.user.is_librarian_user):
        messages.error(request, 'Access denied.')
        return redirect('books:book_list')

    form = BookForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" added successfully! ID: {book.book_id}')
            return redirect('books:book_list')

    return render(request, 'books/book_form.html', {
        'form': form,
        'title': 'Add New Book',
        'button': 'Add Book',
    })


# ─────────────────────────────────────────
# EDIT BOOK
# ─────────────────────────────────────────
@login_required
def book_edit(request, pk):
    if not (request.user.is_admin_user or request.user.is_librarian_user):
        messages.error(request, 'Access denied.')
        return redirect('books:book_list')

    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, request.FILES or None, instance=book)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f'Book "{book.title}" updated successfully!')
            return redirect('books:book_detail', pk=book.pk)

    return render(request, 'books/book_form.html', {
        'form': form,
        'title': f'Edit — {book.title}',
        'button': 'Save Changes',
        'book': book,
    })


# ─────────────────────────────────────────
# DELETE BOOK
# ─────────────────────────────────────────
@login_required
def book_delete(request, pk):
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('books:book_list')

    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'Book "{title}" deleted successfully!')
        return redirect('books:book_list')

    return render(request, 'books/book_confirm_delete.html', {'book': book})


# ─────────────────────────────────────────
# CATEGORY LIST + ADD
# ─────────────────────────────────────────
@login_required
def category_list(request):
    categories = Category.objects.all()
    form = CategoryForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('books:category_list')

    return render(request, 'books/category_list.html', {
        'categories': categories,
        'form': form,
    })


# ─────────────────────────────────────────
# DELETE CATEGORY
# ─────────────────────────────────────────
@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted!')
        return redirect('books:category_list')
    return render(request, 'books/category_confirm_delete.html', {'category': category})