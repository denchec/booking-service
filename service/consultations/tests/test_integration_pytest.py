import pytest
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone

from consultations.models import Consultation


@pytest.mark.django_db
def test_doctor_can_create_consultation_via_post(
    client, now, clinic, doctor_user, doctor
):
    client.force_login(doctor_user)
    url = reverse("consultations:create")
    start_dt = (now + timedelta(days=1)).replace(second=0, microsecond=0)
    data = {
        "clinic": str(clinic.pk),
        "doctor": str(doctor.pk),
        "status": Consultation.CREATED,
        "start_date": start_dt.strftime("%Y-%m-%dT%H:%M"),
    }
    response = client.post(url, data, follow=False)
    assert response.status_code == 302
    assert Consultation.objects.count() == 1
    obj = Consultation.objects.first()
    assert obj.clinic_id == clinic.pk
    assert obj.doctor_id == doctor.pk
    assert obj.status == Consultation.CREATED
    assert obj.start_date == start_dt
    assert obj.end_date == start_dt + timedelta(minutes=30)


@pytest.mark.django_db
def test_admin_can_create_consultation_for_selected_doctor(
    client, now, clinic, admin_user, other_doctor
):
    client.force_login(admin_user)
    url = reverse("consultations:create")
    start_dt = (now + timedelta(days=2)).replace(second=0, microsecond=0)
    data = {
        "clinic": str(clinic.pk),
        "doctor": str(other_doctor.pk),
        "status": Consultation.PENDING,
        "start_date": start_dt.strftime("%Y-%m-%dT%H:%M"),
    }
    response = client.post(url, data, follow=False)
    assert response.status_code == 302
    assert Consultation.objects.count() == 1
    obj = Consultation.objects.first()
    assert obj.doctor_id == other_doctor.pk
    assert obj.status == Consultation.PENDING
    assert obj.end_date == start_dt + timedelta(minutes=30)


@pytest.mark.django_db
def test_patient_cannot_access_create(client, now, clinic, patient_user, doctor):
    client.force_login(patient_user)
    url = reverse("consultations:create")
    response_get = client.get(url)
    assert response_get.status_code == 302

    start_dt = (now + timedelta(days=1)).replace(second=0, microsecond=0)
    data = {
        "clinic": str(clinic.pk),
        "doctor": str(doctor.pk),
        "status": Consultation.CREATED,
        "start_date": start_dt.strftime("%Y-%m-%dT%H:%M"),
    }
    response_post = client.post(url, data, follow=False)
    assert response_post.status_code == 302
    assert Consultation.objects.count() == 0


@pytest.mark.django_db
def test_register_patient_to_future_consultation(
    client, clinic, doctor, patient_user, patient
):
    now = timezone.now()
    consult = Consultation.objects.create(
        clinic=clinic,
        doctor=doctor,
        patient=None,
        status=Consultation.CREATED,
        start_date=now + timedelta(days=1),
        end_date=now + timedelta(days=1, minutes=30),
    )
    client.force_login(patient_user)
    url = reverse("consultations:register", kwargs={"pk": consult.pk})
    response = client.post(url, follow=False)
    assert response.status_code == 302
    consult.refresh_from_db()
    assert consult.patient_id == patient.pk
    assert consult.status == Consultation.CONFIRMED


@pytest.mark.django_db
def test_register_patient_denied_for_past_or_taken(
    client, clinic, doctor, patient_user, patient
):
    now = timezone.now()
    past = Consultation.objects.create(
        clinic=clinic,
        doctor=doctor,
        patient=None,
        status=Consultation.CREATED,
        start_date=now - timedelta(days=1),
        end_date=now - timedelta(days=1) + timedelta(minutes=30),
    )
    taken = Consultation.objects.create(
        clinic=clinic,
        doctor=doctor,
        patient=patient,
        status=Consultation.CONFIRMED,
        start_date=now + timedelta(days=1),
        end_date=now + timedelta(days=1, minutes=30),
    )
    client.force_login(patient_user)

    resp1 = client.post(reverse("consultations:register", kwargs={"pk": past.pk}))
    assert resp1.status_code == 302
    past.refresh_from_db()
    assert past.patient is None
    assert past.status == Consultation.CREATED

    resp2 = client.post(reverse("consultations:register", kwargs={"pk": taken.pk}))
    assert resp2.status_code == 302
    taken.refresh_from_db()
    assert taken.patient_id == patient.pk
    assert taken.status == Consultation.CONFIRMED


@pytest.mark.django_db
def test_list_view_filters_only_without_patient_and_search(
    client, now, clinic, admin_user, doctor, other_doctor, patient
):
    empty_one = Consultation.objects.create(
        clinic=clinic,
        doctor=doctor,
        patient=None,
        status=Consultation.CREATED,
        start_date=now + timedelta(days=3),
        end_date=now + timedelta(days=3, minutes=30),
    )
    Consultation.objects.create(
        clinic=clinic,
        doctor=other_doctor,
        patient=None,
        status=Consultation.CREATED,
        start_date=now + timedelta(days=4),
        end_date=now + timedelta(days=4, minutes=30),
    )
    Consultation.objects.create(
        clinic=clinic,
        doctor=doctor,
        patient=patient,
        status=Consultation.CONFIRMED,
        start_date=now + timedelta(days=5),
        end_date=now + timedelta(days=5, minutes=30),
    )
    client.force_login(admin_user)
    url_all = reverse("consultations:list")
    response_all = client.get(url_all)
    assert response_all.status_code == 200
    ids = {obj.pk for obj in response_all.context["object_list"]}
    assert empty_one.pk in ids

    response_search = client.get(f"{url_all}?q=Doc")
    assert response_search.status_code == 200
    ids_search = {obj.pk for obj in response_search.context["object_list"]}
    assert empty_one.pk in ids_search


@pytest.mark.django_db
def test_update_delete_permissions_and_queryset(
    client, now, clinic, doctor_user, doctor, other_doctor
):
    own = Consultation.objects.create(
        clinic=clinic,
        doctor=doctor,
        patient=None,
        status=Consultation.CREATED,
        start_date=now + timedelta(days=1),
        end_date=now + timedelta(days=1, minutes=30),
    )
    foreign = Consultation.objects.create(
        clinic=clinic,
        doctor=other_doctor,
        patient=None,
        status=Consultation.CREATED,
        start_date=now + timedelta(days=2),
        end_date=now + timedelta(days=2, minutes=30),
    )
    client.force_login(doctor_user)
    resp_upd_own = client.get(reverse("consultations:update", kwargs={"pk": own.pk}))
    resp_del_own = client.get(reverse("consultations:delete", kwargs={"pk": own.pk}))
    assert resp_upd_own.status_code == 200
    assert resp_del_own.status_code == 200

    resp_upd_foreign = client.get(
        reverse("consultations:update", kwargs={"pk": foreign.pk})
    )
    resp_del_foreign = client.get(
        reverse("consultations:delete", kwargs={"pk": foreign.pk})
    )
    assert resp_upd_foreign.status_code == 404
    assert resp_del_foreign.status_code == 404


@pytest.mark.django_db
def test_delete_own_consultation_via_post(client, now, clinic, doctor_user, doctor):
    consult = Consultation.objects.create(
        clinic=clinic,
        doctor=doctor,
        patient=None,
        status=Consultation.CREATED,
        start_date=now + timedelta(days=1),
        end_date=now + timedelta(days=1, minutes=30),
    )
    client.force_login(doctor_user)
    url = reverse("consultations:delete", kwargs={"pk": consult.pk})
    response = client.post(url, data={}, follow=False)
    assert response.status_code == 302
    assert not Consultation.objects.filter(pk=consult.pk).exists()


@pytest.mark.django_db
def test_upcoming_list_context_for_doctor_and_patient(
    client, now, clinic, doctor_user, doctor, other_doctor, patient_user, patient
):
    c1 = Consultation.objects.create(
        clinic=clinic,
        doctor=doctor,
        patient=patient,
        status=Consultation.CONFIRMED,
        start_date=now + timedelta(days=1),
        end_date=now + timedelta(days=1, minutes=30),
    )
    c2 = Consultation.objects.create(
        clinic=clinic,
        doctor=doctor,
        patient=patient,
        status=Consultation.STARTED,
        start_date=now + timedelta(days=2),
        end_date=now + timedelta(days=2, minutes=30),
    )
    Consultation.objects.create(
        clinic=clinic,
        doctor=other_doctor,
        patient=patient,
        status=Consultation.CONFIRMED,
        start_date=now + timedelta(days=3),
        end_date=now + timedelta(days=3, minutes=30),
    )
    url = reverse("consultations:list")

    client.force_login(doctor_user)
    resp_doc = client.get(url)
    assert resp_doc.status_code == 200
    upcoming = resp_doc.context.get("upcoming_list")
    title = resp_doc.context.get("upcoming_title")
    assert upcoming is not None
    ids = {obj.pk for obj in upcoming}
    assert c1.pk in ids and c2.pk in ids
    assert title == "Ближайшие консультации с пациентами"

    client.force_login(patient_user)
    resp_pat = client.get(url)
    assert resp_pat.status_code == 200
    upcoming_p = resp_pat.context.get("upcoming_list")
    title_p = resp_pat.context.get("upcoming_title")
    assert upcoming_p is not None
    ids_p = {obj.pk for obj in upcoming_p}
    assert c1.pk in ids_p and c2.pk in ids_p
    assert title_p == "Мои ближайшие консультации"


@pytest.mark.django_db
def test_change_consultation_status_logic(clinic, doctor):
    now = timezone.now()
    completed = Consultation.objects.create(
        clinic=clinic,
        doctor=doctor,
        status=Consultation.STARTED,
        start_date=now - timedelta(hours=2),
        end_date=now - timedelta(hours=1),
    )
    started = Consultation.objects.create(
        clinic=clinic,
        doctor=doctor,
        status=Consultation.PENDING,
        start_date=now - timedelta(minutes=10),
        end_date=now + timedelta(minutes=20),
    )
    future = Consultation.objects.create(
        clinic=clinic,
        doctor=doctor,
        status=Consultation.CREATED,
        start_date=now + timedelta(hours=3),
        end_date=now + timedelta(hours=3, minutes=30),
    )
    from consultations.tasks import change_consultation_status

    change_consultation_status()

    completed.refresh_from_db()
    started.refresh_from_db()
    future.refresh_from_db()
    assert completed.status == Consultation.COMPLETED
    assert started.status == Consultation.STARTED
    assert future.status == Consultation.CREATED


@pytest.mark.django_db
def test_delete_expired_consultations_logic(clinic, doctor):
    now = timezone.now()
    expired = Consultation.objects.create(
        clinic=clinic,
        doctor=doctor,
        status=Consultation.CREATED,
        start_date=now - timedelta(days=1),
        end_date=now - timedelta(days=1) + timedelta(minutes=30),
    )
    keep = Consultation.objects.create(
        clinic=clinic,
        doctor=doctor,
        status=Consultation.PENDING,
        start_date=now - timedelta(days=1),
        end_date=now - timedelta(days=1) + timedelta(minutes=30),
    )
    from consultations.tasks import delete_expired_consultations

    delete_expired_consultations()
    assert not Consultation.objects.filter(pk=expired.pk).exists()
    assert Consultation.objects.filter(pk=keep.pk).exists()
