from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
)
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
import re

from consultations.models import Consultation
from consultations.forms import ConsultationCreateForm
from users.models import User, Doctor, Patient


class ConsultationQuerysetMixin:
    """
    Ограничивает доступ к данным:
    - admin/is_staff: видят всё
    - doctor: только свои консультации
    """

    def get_queryset(self):
        base_qs = Consultation.objects.select_related(
            "clinic", "doctor", "doctor__user", "patient", "patient__user"
        ).order_by("-start_date")
        user = self.request.user

        if (
            getattr(user, "is_staff", False)
            or getattr(user, "role", None) == User.ADMIN
        ):
            return base_qs

        if getattr(user, "role", None) == User.DOCTOR:
            try:
                doctor = Doctor.objects.get(user=user)
            except Doctor.DoesNotExist:
                return base_qs.none()
            return base_qs.filter(doctor=doctor)

        return base_qs.none()


class ConsultationListView(LoginRequiredMixin, ListView):
    model = Consultation
    paginate_by = 20
    template_name = "consultations/list.html"

    def get_queryset(self):
        qs = Consultation.objects.select_related(
            "clinic", "doctor", "doctor__user", "patient", "patient__user"
        ).filter(patient__isnull=True)

        # Query params
        q = self.request.GET.get("q", "").strip()
        status_param = self.request.GET.get("status", "").strip()
        sort = self.request.GET.get("sort", "").strip()
        order = self.request.GET.get("order", "desc").strip()

        # Фильтрация по статусу
        if status_param:
            raw_statuses = [s.strip() for s in status_param.split(",") if s.strip()]
            if raw_statuses:
                qs = qs.filter(status__in=raw_statuses)

        # Поиск по ФИО врача и пациента
        if q:
            tokens = [t for t in re.split(r"\s+", q) if t]
            for tok in tokens:
                token_q = (
                    Q(doctor__user__first_name__icontains=tok)
                    | Q(doctor__user__middle_name__icontains=tok)
                    | Q(doctor__user__last_name__icontains=tok)
                    | Q(patient__user__first_name__icontains=tok)
                    | Q(patient__user__middle_name__icontains=tok)
                    | Q(patient__user__last_name__icontains=tok)
                )
                qs = qs.filter(token_q)

        # Сортировка
        if sort == "created":
            if order == "asc":
                qs = qs.order_by("created_at")
            else:
                qs = qs.order_by("-created_at")
        elif sort == "status":
            if order == "asc":
                qs = qs.order_by("status", "start_date")
            else:
                qs = qs.order_by("-status", "-start_date")
        elif sort == "start_date":
            if order == "asc":
                qs = qs.order_by("start_date")
            else:
                qs = qs.order_by("-start_date")
        else:
            qs = qs.order_by("start_date")

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()

        upcoming = Consultation.objects.select_related(
            "clinic", "doctor", "doctor__user", "patient", "patient__user"
        ).filter(patient__isnull=False)

        # Поиск по ФИО врача/пациента для блока ближайших консультаций
        q = self.request.GET.get("q", "").strip()
        if q:
            tokens = [t for t in re.split(r"\s+", q) if t]
            for tok in tokens:
                token_q = (
                    Q(doctor__user__first_name__icontains=tok)
                    | Q(doctor__user__middle_name__icontains=tok)
                    | Q(doctor__user__last_name__icontains=tok)
                    | Q(patient__user__first_name__icontains=tok)
                    | Q(patient__user__middle_name__icontains=tok)
                    | Q(patient__user__last_name__icontains=tok)
                )
                upcoming = upcoming.filter(token_q)

        # Сортировка для блока ближайших консультаций
        sort = self.request.GET.get("sort", "").strip()
        order = self.request.GET.get("order", "asc").strip()

        def order_upcoming(qs):
            if sort == "status":
                return (
                    qs.order_by("status", "start_date")
                    if order == "asc"
                    else qs.order_by("-status", "-start_date")
                )
            if sort == "start_date":
                return (
                    qs.order_by("start_date")
                    if order == "asc"
                    else qs.order_by("-start_date")
                )
            return qs.order_by("start_date")

        if getattr(user, "role", None) == User.DOCTOR:
            try:
                doctor = Doctor.objects.get(user=user)
            except Doctor.DoesNotExist:
                doctor = None
            if doctor is not None:
                context["upcoming_list"] = order_upcoming(
                    upcoming.filter(doctor=doctor)
                )[:20]
                context["upcoming_title"] = "Ближайшие консультации с пациентами"
        elif getattr(user, "role", None) == User.PATIENT:
            try:
                patient = Patient.objects.get(user=user)
            except Patient.DoesNotExist:
                patient = None
            if patient is not None:
                context["upcoming_list"] = order_upcoming(
                    upcoming.filter(patient=patient)
                )[:20]
                context["upcoming_title"] = "Мои ближайшие консультации"

        context["now"] = now
        context["is_admin"] = (
            getattr(user, "is_staff", False)
            or getattr(user, "role", None) == User.ADMIN
        )
        context["is_doctor"] = getattr(user, "role", None) == User.DOCTOR
        context["is_patient"] = getattr(user, "role", None) == User.PATIENT

        params = self.request.GET.copy()
        if "page" in params:
            for _ in range(len(params.getlist("page"))):
                try:
                    del params["page"]
                except Exception:
                    break

        context["query_without_page"] = params.urlencode()
        context["current_q"] = self.request.GET.get("q", "").strip()
        context["current_sort"] = self.request.GET.get("sort", "").strip()
        context["current_order"] = self.request.GET.get("order", "asc").strip()
        context["current_status"] = self.request.GET.get("status", "").strip()

        return context


class ConsultationDetailView(LoginRequiredMixin, DetailView):
    model = Consultation
    template_name = "consultations/detail.html"

    def get_queryset(self):
        return Consultation.objects.select_related(
            "clinic", "doctor", "doctor__user", "patient", "patient__user"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj: Consultation = self.object
        user = self.request.user
        can_register = False

        if (
            getattr(user, "role", None) == User.PATIENT
            and obj.patient is None
            and obj.start_date > timezone.now()
        ):
            # есть профиль пациента
            can_register = Patient.objects.filter(user=user).exists()
        context["can_register"] = can_register
        return context


class ConsultationCreateView(LoginRequiredMixin, View):
    form_class = ConsultationCreateForm
    success_url = reverse_lazy("consultations:list")
    template_name = "consultations/form.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        # Разрешаем только доктору и админу
        if not (
            getattr(user, "is_staff", False)
            or getattr(user, "role", None) in (User.ADMIN, User.DOCTOR)
        ):
            return redirect("consultations:list")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, user=request.user)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        clinic = form.cleaned_data["clinic"]
        user_role = getattr(request.user, "role", None)
        if user_role == User.DOCTOR and not getattr(request.user, "is_staff", False):
            try:
                doctor = Doctor.objects.get(user=request.user)
            except Doctor.DoesNotExist:
                form.add_error(None, "Для вашего пользователя не найден профиль врача.")
                return render(request, self.template_name, {"form": form})
        else:
            doctor = form.cleaned_data.get("doctor")
            if doctor is None:
                form.add_error("doctor", "Необходимо выбрать врача.")
                return render(request, self.template_name, {"form": form})

        start_date = form.cleaned_data["start_date"]

        status = form.cleaned_data["status"]
        end_date = start_date + timedelta(minutes=30)

        Consultation.objects.create(
            clinic=clinic,
            doctor=doctor,
            status=status,
            start_date=start_date,
            end_date=end_date,
        )

        return redirect(self.success_url)


class ConsultationUpdateView(LoginRequiredMixin, ConsultationQuerysetMixin, UpdateView):
    model = Consultation
    fields = ["clinic", "doctor", "patient", "status", "start_date", "end_date"]
    success_url = reverse_lazy("consultations:list")
    template_name = "consultations/form.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        # Разрешаем только доктору и админу
        if not (
            getattr(user, "is_staff", False)
            or getattr(user, "role", None) in (User.ADMIN, User.DOCTOR)
        ):
            return redirect("consultations:list")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset()


class ConsultationDeleteView(LoginRequiredMixin, ConsultationQuerysetMixin, DeleteView):
    model = Consultation
    success_url = reverse_lazy("consultations:list")
    template_name = "consultations/confirm_delete.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        # Разрешаем только доктору и админу
        if not (
            getattr(user, "is_staff", False)
            or getattr(user, "role", None) in (User.ADMIN, User.DOCTOR)
        ):
            return redirect("consultations:list")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset()


class ConsultationRegisterView(LoginRequiredMixin, View):
    success_url = reverse_lazy("consultations:list")

    def post(self, request, pk, *args, **kwargs):
        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            return redirect(self.success_url)

        try:
            consultation = Consultation.objects.select_related("patient").get(pk=pk)
        except Consultation.DoesNotExist:
            return redirect(self.success_url)

        if (
            getattr(request.user, "role", None) == User.PATIENT
            and consultation.patient is None
            and consultation.start_date > timezone.now()
        ):
            consultation.patient = patient
            consultation.status = Consultation.CONFIRMED
            consultation.save(update_fields=["patient", "status"])
            return redirect(self.success_url)

        return redirect(self.success_url)
