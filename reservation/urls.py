from django.urls import path
from . import views

app_name = 'reservation'

urlpatterns = [
    path('', views.reservation_list, name='reservation_list'),
    path('reserve/<int:book_id>/', views.reserve_book, name='reserve_book'),
    path('cancel/<int:pk>/', views.cancel_reservation, name='cancel_reservation'),
    path('mark-ready/<int:pk>/', views.mark_ready, name='mark_ready'),
    path('fulfill/<int:pk>/', views.fulfill_reservation, name='fulfill_reservation'),
]