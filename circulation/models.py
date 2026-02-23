

# Create your models here.
from django.db import models
from django.utils import timezone
from accounts.models import User
from books.models import Book
from datetime import timedelta


class IssuedBook(models.Model):
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issued_records')
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_by_staff')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now().date() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status == 'returned':
            return False
        return timezone.now().date() > self.due_date

    @property
    def overdue_days(self):
        if self.status == 'returned' and self.return_date:
            delta = self.return_date - self.due_date
        elif self.is_overdue:
            delta = timezone.now().date() - self.due_date
        else:
            return 0
        return max(0, delta.days)

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.book.title}"

    class Meta:
        ordering = ['-issue_date']


class Fine(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('waived', 'Waived'),
    ]

    issued_book = models.OneToOneField(IssuedBook, on_delete=models.CASCADE, related_name='fine')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fines')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    overdue_days = models.IntegerField(default=0)
    fine_per_day = models.DecimalField(max_digits=5, decimal_places=2, default=2.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='fines_cleared')
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Fine for {self.student.get_full_name()} - ₹{self.amount}"

    class Meta:
        ordering = ['-created_at']


class FineSettings(models.Model):
    fine_per_day = models.DecimalField(max_digits=5, decimal_places=2, default=2.00)
    loan_period_days = models.IntegerField(default=14)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Fine: ₹{self.fine_per_day}/day | Loan: {self.loan_period_days} days"

    class Meta:
        verbose_name = "Fine Setting"
        verbose_name_plural = "Fine Settings"