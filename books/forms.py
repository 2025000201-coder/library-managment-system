from django import forms
from .models import Book, Category, Publisher


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['name', 'address', 'website']
        widgets = {
            'name':    forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'category', 'publisher',
                  'total_copies', 'available_copies', 'rack_number',
                  'cover_image', 'description']
        widgets = {
            'title':            forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Book title'}),
            'author':           forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author name'}),
            'isbn':             forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ISBN number'}),
            'category':         forms.Select(attrs={'class': 'form-select'}),
            'publisher':        forms.Select(attrs={'class': 'form-select'}),
            'total_copies':     forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'rack_number':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. A-12'}),
            'cover_image':      forms.FileInput(attrs={'class': 'form-control'}),
            'description':      forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                                      'placeholder': 'Short description of the book'}),
        }
