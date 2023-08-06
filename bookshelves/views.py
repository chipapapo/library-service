from rest_framework import viewsets

from bookshelves.models import Book
from bookshelves.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
