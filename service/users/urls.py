from django.urls import include, path
from rest_framework.routers import SimpleRouter
from users.views import UserViewSet

router = SimpleRouter()
router.register("", UserViewSet)

urlpatterns = [
    path("token/", include("users.token.urls")),
    path("", include(router.urls)),
]
