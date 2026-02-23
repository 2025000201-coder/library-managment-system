from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Book, Category, Publisher


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'website']
    search_fields = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['book_id', 'title', 'author', 'category',
                    'total_copies', 'available_copies', 'date_added']
    list_filter = ['category', 'date_added']
    search_fields = ['title', 'author', 'isbn', 'book_id']
    readonly_fields = ['book_id', 'date_added']