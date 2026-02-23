from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from books.models import Book, Category
from accounts.models import User
from datetime import date
import json


@login_required
def home(request):
    today           = date.today()
    total_books     = Book.objects.count()
    total_students  = User.objects.filter(role='student').count()
    total_users     = User.objects.count()
    total_available = Book.objects.filter(available_copies__gt=0).count()

    try:
        from circulation.models import IssuedBook, Fine
        total_issued      = IssuedBook.objects.filter(status='issued').count()
        total_overdue     = IssuedBook.objects.filter(status='issued', due_date__lt=today).count()
        total_returned    = IssuedBook.objects.filter(status='returned').count()
        total_unpaid_fines = Fine.objects.filter(status='unpaid').count()
        total_fine_amount = sum(f.amount for f in Fine.objects.filter(status='unpaid'))
        recent_issues     = IssuedBook.objects.select_related('book', 'student').order_by('-issue_date')[:6]
        overdue_list      = IssuedBook.objects.select_related('book', 'student').filter(
                                status='issued', due_date__lt=today
                            ).order_by('due_date')[:5]
    except Exception:
        total_issued = total_overdue = total_returned = 0
        total_unpaid_fines = total_fine_amount = 0
        recent_issues = []
        overdue_list  = []

    recent_books = Book.objects.select_related('category').order_by('-date_added')[:6]

    # Chart data
    color_palette = [
        '#4361ee','#06d6a0','#3a86ff',
        '#fb5607','#ffbe0b','#8338ec',
        '#ef233c','#2ec4b6'
    ]
    categories = list(Category.objects.all())
    cat_data   = sorted(
        [(cat.name, Book.objects.filter(category=cat).count()) for cat in categories],
        key=lambda x: x[1], reverse=True
    )[:8]

    cat_labels = [c[0] for c in cat_data]
    cat_counts = [c[1] for c in cat_data]
    cat_colors = color_palette[:len(cat_data)]

    context = {
        'today':             today,
        'total_books':       total_books,
        'total_students':    total_students,
        'total_users':       total_users,
        'total_available':   total_available,
        'total_issued':      total_issued,
        'total_overdue':     total_overdue,
        'total_returned':    total_returned,
        'total_unpaid_fines': total_unpaid_fines,
        'total_fine_amount': total_fine_amount,
        'recent_books':      recent_books,
        'recent_issues':     recent_issues,
        'overdue_list':      overdue_list,
        'cat_labels':        json.dumps(cat_labels),
        'cat_counts':        json.dumps(cat_counts),
        'cat_colors':        json.dumps(cat_colors),
    }
    return render(request, 'dashboard/dashboard.html', context)