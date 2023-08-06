from rest_framework import serializers
from rest_framework.exceptions import APIException

from borrowings.models import Borrowing
from bookshelves.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingListSerializer(BorrowingSerializer):
    book = BookSerializer(many=False, read_only=True)
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingCreateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )

    def create(self, validated_data):
        book = validated_data["book"]

        if book.inventory > 0:
            book.inventory = book.inventory - 1
            book.save()
            return Borrowing.objects.create(**validated_data)

        raise APIException("The book is not available")
