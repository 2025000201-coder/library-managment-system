from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('export/issued/excel/', views.export_issued_excel, name='export_issued_excel'),
    path('export/issued/pdf/', views.export_issued_pdf, name='export_issued_pdf'),
    path('export/fines/excel/', views.export_fines_excel, name='export_fines_excel'),
    path('export/fines/pdf/', views.export_fines_pdf, name='export_fines_pdf'),
    path('export/books/excel/', views.export_books_excel, name='export_books_excel'),
    path('export/overdue/pdf/', views.export_overdue_pdf, name='export_overdue_pdf'),
]