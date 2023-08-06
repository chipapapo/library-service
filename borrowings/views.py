from datetime import datetime

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
)
from user.permissions import IsAdminOrIfAuthenticatedReadOnly


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset

        is_active = self.request.query_params.get("is-active")

        if is_active == "true":
            queryset = queryset.filter(actual_return_date__isnull=True)

        if self.request.user.is_staff:
            borrow_date = self.request.query_params.get("borrow-date")
            user_id_str = self.request.query_params.get("user")

            if borrow_date:
                queryset = queryset.filter(borrow_date=borrow_date)

            if user_id_str:
                queryset = queryset.filter(user_id=int(user_id_str))

            return queryset

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return BorrowingListSerializer
        if self.action == "create":
            return BorrowingCreateSerializer

        return BorrowingSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="is-active",
                description="Filter by not returned book",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="borrow-date",
                description="Filter by date of borrowing",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="user", description="Filter by user", required=False, type=int
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
