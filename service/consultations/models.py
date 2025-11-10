from django.db import models

from users.models import Doctor, Patient


class Clinic(models.Model):
    name = models.CharField(max_length=150, blank=False)
    legal_address = models.CharField(max_length=150, blank=False)
    actual_address = models.CharField(max_length=150, blank=False)

    def __str__(self):
        return self.name


class Consultation(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=True)

    CONFIRMED = "подтверждена"
    PENDING = "ожидает"
    STARTED = "начата"
    COMPLETED = "завершена"
    PAID = "оплачена"
    CREATED = "создана"
    STATUS_CHOICES = [
        (CONFIRMED, "Подтверждена"),
        (PENDING, "Ожидает"),
        (STARTED, "Начата"),
        (COMPLETED, "Завершена"),
        (PAID, "Оплачена"),
        (CREATED, "Создана"),
    ]

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=CREATED, blank=False
    )

    start_date = models.DateTimeField(blank=False)
    end_date = models.DateTimeField(blank=False)
