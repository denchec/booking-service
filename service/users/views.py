from rest_framework import viewsets
from users.serializers import UserSerializer
from users.models import User


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "public_id"

    def filter_queryset(self, queryset):
        # Configure here who can manage which users
        if self.request.user.is_superuser:
            return super().filter_queryset(queryset)

        return (
            super()
            .filter_queryset(queryset)
            .filter(public_id=self.request.user.public_id)
        )
