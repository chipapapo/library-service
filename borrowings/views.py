from datetime import datetime

from rest_framework import viewsets

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingCreateSerializer
from user.permissions import IsAdminOrIfAuthenticatedReadOnly


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.is_staff:
            date = self.request.query_params.get("date")
            user_id_str = self.request.query_params.get("user")

            if date:
                date = datetime.strptime(date, "%Y-%m-%d").date()
                queryset = queryset.filter(show_time__date=date)

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
