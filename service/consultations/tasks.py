from celery import shared_task

from consultations.models import Consultation
from django.utils import timezone


def change_consultation_status():
    consultations = Consultation.objects.filter()
    for consultation in consultations:
        if consultation.end_date < timezone.now():
            consultation.status = Consultation.COMPLETED
            consultation.save()

        elif consultation.start_date <= timezone.now():
            consultation.status = Consultation.STARTED
            consultation.save()


def delete_expired_consultations():
    consultations = Consultation.objects.filter(
        status=Consultation.CREATED, start_date__lt=timezone.now()
    )
    for consultation in consultations:
        consultation.delete()


@shared_task
def check_consultations():
    change_consultation_status()
    delete_expired_consultations()
