from django.contrib.auth.models import AbstractUser
from django.db import models
from service.models import PublicModel


class User(AbstractUser, PublicModel):
    first_name = models.CharField(max_length=150, blank=False)
    middle_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    phone = models.CharField(max_length=150, blank=False)
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
        max_length=20,
        choices=ROLE_CHOICES,
        default=PATIENT,
        blank=False
        )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.role})"
