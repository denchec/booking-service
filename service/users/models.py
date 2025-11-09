from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from service.models import PublicModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email должен быть указан")
        email = self.normalize_email(email)
        # Для совместимости с AbstractUser оставляем username в БД,
        # но автоматически заполняем его email и нигде не используем явно.
        extra_fields.setdefault("username", email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, PublicModel):
    first_name = models.CharField(max_length=150, blank=False)
    middle_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(unique=True, blank=False)

    DOCTOR = "doctor"
    PATIENT = "patient"
    ADMIN = "admin"
    ROLE_CHOICES = [
        (DOCTOR, "Doctor"),
        (PATIENT, "Patient"),
        (ADMIN, "Admin"),
    ]

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default=PATIENT, blank=False
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    speciality = models.CharField(max_length=150, blank=False)


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=150, blank=False)
