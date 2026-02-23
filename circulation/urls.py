from django.urls import path
from . import views

app_name = 'circulation'

urlpatterns = [
    path('issue/', views.issue_book, name='issue_book'),
    path('issued/', views.issued_list, name='issued_list'),
    path('issued/<int:pk>/', views.issued_book_detail, name='issued_book_detail'),
    path('return/<int:pk>/', views.return_book, name='return_book'),
    path('fines/', views.fine_list, name='fine_list'),
    path('fines/<int:pk>/paid/', views.mark_fine_paid, name='mark_fine_paid'),
    path('fines/<int:pk>/waive/', views.waive_fine, name='waive_fine'),
    path('my-books/', views.my_books, name='my_books'),
]