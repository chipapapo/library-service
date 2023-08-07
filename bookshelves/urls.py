from rest_framework import routers

from bookshelves.views import BookViewSet

router = routers.DefaultRouter()
router.register("books", BookViewSet)


urlpatterns = router.urls

app_name = "bookshelves"
