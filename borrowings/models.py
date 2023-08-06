from django.db import models

from bookshelves.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(
        Book, related_name="borrowings", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, related_name="borrowings", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.book.title} return by {self.expected_return_date}"
