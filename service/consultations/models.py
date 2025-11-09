from django.db import models

from users.models import Doctor, Patient


class Clinic(models.Model):
    name = models.CharField(max_length=150, blank=False)
    legal_address = models.CharField(max_length=150, blank=False)
    actual_address = models.CharField(max_length=150, blank=False)


class Consultation(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    status = models.CharField(max_length=150, blank=False)
    start_date = models.DateTimeField(blank=False)
    end_date = models.DateTimeField(blank=False)
