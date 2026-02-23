from django.contrib import admin
from .models import IssuedBook, Fine, FineSettings


@admin.register(IssuedBook)
class IssuedBookAdmin(admin.ModelAdmin):
    list_display = ('book', 'student', 'issue_date', 'due_date', 'return_date', 'status')
    list_filter = ('status', 'issue_date')
    search_fields = ('book__title', 'student__username', 'student__first_name')
    date_hierarchy = 'issue_date'


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('student', 'issued_book', 'amount', 'overdue_days', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('student__username', 'issued_book__book__title')


@admin.register(FineSettings)
class FineSettingsAdmin(admin.ModelAdmin):
    list_display = ('fine_per_day', 'loan_period_days', 'updated_at')