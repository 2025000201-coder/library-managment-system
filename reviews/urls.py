from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:book_id>/', views.add_review, name='add_review'),
    path('delete/<int:pk>/', views.delete_review, name='delete_review'),
    path('book/<int:book_id>/', views.book_reviews, name='book_reviews'),
]