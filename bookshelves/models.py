from django.db import models


class Book(models.Model):
    COVER_HARDNESS = [
        ("HARD", "Hard cover"),
        ("SOFT", "Soft cover")
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=4, choices=COVER_HARDNESS
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        max_digits=5, decimal_places=2
    )

    def __str__(self):
        return f"{self.title} by {self.author}"
