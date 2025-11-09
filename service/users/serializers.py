from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()

    class Meta:
        model = User
        fields = [
            "public_id",
            "email",
            "first_name",
            "last_name",
            "middle_name",
            "role",
        ]
