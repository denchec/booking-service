import pytest
from django.utils import timezone

from consultations.models import Clinic
from users.models import User, Doctor, Patient


@pytest.fixture
def now():
    return timezone.now()


@pytest.fixture
def clinic(db):
    return Clinic.objects.create(
        name="Clinic One",
        legal_address="Legal Addr",
        actual_address="Actual Addr",
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email="admin@example.com",
        password="adminpass",
        first_name="Admin",
        middle_name="A",
        last_name="User",
        role=User.ADMIN,
        is_staff=False,
    )


@pytest.fixture
def doctor_user(db):
    return User.objects.create_user(
        email="doc@example.com",
        password="docpass",
        first_name="Doc",
        middle_name="D",
        last_name="User",
        role=User.DOCTOR,
    )


@pytest.fixture
def doctor(db, doctor_user):
    return Doctor.objects.create(user=doctor_user, speciality="Therapist")


@pytest.fixture
def other_doctor_user(db):
    return User.objects.create_user(
        email="doc2@example.com",
        password="docpass",
        first_name="John",
        middle_name="Q",
        last_name="Doe",
        role=User.DOCTOR,
    )


@pytest.fixture
def other_doctor(db, other_doctor_user):
    return Doctor.objects.create(user=other_doctor_user, speciality="Cardio")


@pytest.fixture
def patient_user(db):
    return User.objects.create_user(
        email="pat@example.com",
        password="patpass",
        first_name="Pat",
        middle_name="P",
        last_name="User",
        role=User.PATIENT,
    )


@pytest.fixture
def patient(db, patient_user):
    return Patient.objects.create(user=patient_user, phone="79991234567")
