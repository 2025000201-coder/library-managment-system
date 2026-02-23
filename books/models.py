from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    book_id = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL,
                                  null=True, blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    rack_number = models.CharField(max_length=20, blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    description = models.TextField(blank=True)
    date_added = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.book_id:
            last = Book.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.book_id = f"LIB-{next_id:04d}"
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        return self.available_copies > 0

    def __str__(self):
        return f"{self.title} by {self.author}"