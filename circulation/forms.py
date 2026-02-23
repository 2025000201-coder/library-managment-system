from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import IssuedBook, FineSettings
from books.models import Book
from accounts.models import User


class IssueBookForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(role='student').order_by('first_name'),
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        label='Student'
    )
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(available_copies__gt=0).order_by('title'),
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        label='Book'
    )
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=timezone.now().date() + timedelta(days=14),
        label='Due Date'
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes...'})
    )

    class Meta:
        model = IssuedBook
        fields = ['student', 'book', 'due_date', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['due_date'].initial = (timezone.now() + timedelta(days=14)).date()


class FineSettingsForm(forms.ModelForm):
    class Meta:
        model = FineSettings
        fields = ['fine_per_day', 'loan_period_days']
        widgets = {
            'fine_per_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.50', 'min': '0'}),
            'loan_period_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '60'}),
        }
        labels = {
            'fine_per_day': 'Fine per day (₹)',
            'loan_period_days': 'Default loan period (days)',
        }