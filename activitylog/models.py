from django.db import models
from accounts.models import User


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('book_added', 'Book Added'),
        ('book_edited', 'Book Edited'),
        ('book_deleted', 'Book Deleted'),
        ('book_issued', 'Book Issued'),
        ('book_returned', 'Book Returned'),
        ('fine_paid', 'Fine Marked Paid'),
        ('fine_waived', 'Fine Waived'),
        ('user_added', 'User Added'),
        ('user_edited', 'User Edited'),
        ('user_deleted', 'User Deleted'),
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} — {self.get_action_display()} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']


ACTION_ICONS = {
    'book_added': ('bi-plus-circle', 'success'),
    'book_edited': ('bi-pencil', 'primary'),
    'book_deleted': ('bi-trash', 'danger'),
    'book_issued': ('bi-arrow-right-circle', 'info'),
    'book_returned': ('bi-arrow-return-left', 'success'),
    'fine_paid': ('bi-check-circle', 'success'),
    'fine_waived': ('bi-x-circle', 'secondary'),
    'user_added': ('bi-person-plus', 'success'),
    'user_edited': ('bi-person-gear', 'primary'),
    'user_deleted': ('bi-person-x', 'danger'),
    'user_login': ('bi-box-arrow-in-right', 'primary'),
    'user_logout': ('bi-box-arrow-right', 'secondary'),
}