from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer
from bookshelves.tests.test_books import sample_book


BORROWING_URL = reverse("checkout:borrowing-list")

def sample_borrowing(user, **params):
    date = datetime.strptime("2023-12-23", "%Y-%m-%d").date()
    book = sample_book()
    defaults = {
        "expected_return_date": date,
        "book": book,
        "user": user,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


def detail_url(borrowing_id):
    return reverse("checkout:borrowing-detail", args=[borrowing_id])


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_borrowings(self):
        sample_borrowing(self.user)
        sample_borrowing(self.user)

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.order_by("id")
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_borrowings_by_is_active(self):
        date = datetime.strptime("2023-12-24", "%Y-%m-%d").date()
        borrowing1 = sample_borrowing(self.user, actual_return_date=date)
        borrowing2 = sample_borrowing(self.user, actual_return_date=date)

        borrowing3 = sample_borrowing(self.user)
        borrowing4 = sample_borrowing(self.user)

        res = self.client.get(
            BORROWING_URL, {"is-active": f"true"}
        )

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)
        serializer3 = BorrowingListSerializer(borrowing3)
        serializer4 = BorrowingListSerializer(borrowing4)

        self.assertNotIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        self.assertIn(serializer3.data, res.data)
        self.assertIn(serializer4.data, res.data)

    def test_filter_borrowings_by_borrow_date_not_applicable(self):
        date = datetime.strptime("2023-12-24", "%Y-%m-%d").date()

        borrowing1 = sample_borrowing(self.user)
        borrowing2 = sample_borrowing(self.user)

        borrowing3 = sample_borrowing(self.user, borrow_date=date)

        res = self.client.get(
            BORROWING_URL, {"borrow-date": str(date)}
        )

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)
        serializer3 = BorrowingListSerializer(borrowing3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertIn(serializer3.data, res.data)

    def test_only_user_borrowings_and_filter_borrowings_by_user_not_applicable(self):
        user = get_user_model().objects.create_user(
            "user@user.com",
            "testpass",
        )
        user1 = get_user_model().objects.create_user(
            "user1@user.com",
            "testpass",
        )

        borrowing1 = sample_borrowing(self.user)
        borrowing2 = sample_borrowing(self.user)

        borrowing3 = sample_borrowing(user)

        res = self.client.get(
            BORROWING_URL, {"user": self.user.id}
        )

        borrowing4 = sample_borrowing(user1)

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)
        serializer3 = BorrowingListSerializer(borrowing3)
        serializer4 = BorrowingListSerializer(borrowing4)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
        self.assertNotIn(serializer4.data, res.data)

    def test_create_borrowing_forbidden(self):
        date = datetime.strptime("2023-12-23", "%Y-%m-%d").date()
        book = sample_book()
        payload = {
            "expected_return_date": date,
            "book": book,
            "user": self.user,
        }
        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_movie(self):
        date = datetime.strptime("2023-12-23", "%Y-%m-%d").date()
        book = sample_book()
        payload = {
            "expected_return_date": date,
            "book": book.id,
            "user": self.user.id,
        }
        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_filter_borrowings_by_borrow_date(self):
        date = datetime.strptime("2023-12-24", "%Y-%m-%d").date()

        borrowing1 = sample_borrowing(self.user)
        borrowing2 = sample_borrowing(self.user)

        borrowing3 = sample_borrowing(self.user)
        borrowing3.borrow_date = date
        borrowing3.save()

        res = self.client.get(
            BORROWING_URL, {"borrow-date": date}
        )

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)
        serializer3 = BorrowingListSerializer(borrowing3)

        self.assertNotIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        self.assertIn(serializer3.data, res.data)

    def test_only_user_borrowings_and_filter_borrowings_by_user(self):
        user = get_user_model().objects.create_user(
            "user@user.com",
            "testpass",
        )
        user1 = get_user_model().objects.create_user(
            "user1@user.com",
            "testpass",
        )

        borrowing1 = sample_borrowing(self.user)
        borrowing2 = sample_borrowing(self.user)

        borrowing3 = sample_borrowing(user)

        res = self.client.get(
            BORROWING_URL, {"user": user.id}
        )

        borrowing4 = sample_borrowing(user1)

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)
        serializer3 = BorrowingListSerializer(borrowing3)
        serializer4 = BorrowingListSerializer(borrowing4)

        self.assertNotIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        self.assertIn(serializer3.data, res.data)
        self.assertNotIn(serializer4.data, res.data)
