from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ready', 'Ready for Pickup'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    reserved_on = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-reserved_on']

    def __str__(self):
        return f"{self.user.get_full_name()} → {self.book.title} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.expires_on:
            self.expires_on = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def mark_ready(self):
        self.status = 'ready'
        self.expires_on = timezone.now() + timedelta(days=3)
        self.save()

    def cancel(self):
        self.status = 'cancelled'
        self.save()

    def is_expired(self):
        return self.expires_on < timezone.now() and self.status not in ('fulfilled', 'cancelled', 'expired')