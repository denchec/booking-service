from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from rest_framework import viewsets
from users.serializers import UserSerializer
from users.models import User, Doctor, Patient
from django.contrib.auth.mixins import LoginRequiredMixin


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


class AuthView(View):
    template_name = "users/login.html"

    def get(self, request):
        """Отображение формы логина"""
        return render(request, self.template_name)

    def post(self, request):
        """Обработка логина"""
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        return render(
            request,
            self.template_name,
            {"error": "Неверный email или пароль"},
        )


class RegisterView(View):
    template_name = "users/register.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        first_name = request.POST.get("first_name")
        middle_name = request.POST.get("middle_name")
        last_name = request.POST.get("last_name")
        role = request.POST.get("role")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(
            email=email,
        ).exists():
            return render(
                request,
                self.template_name,
                {"error": "Пользователь с таким email уже существует."},
            )

        user = User.objects.create_user(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            password=password,
            role=role,
        )

        if role == User.DOCTOR:
            speciality = request.POST.get("speciality")
            Doctor.objects.create(
                user=user,
                speciality=speciality,
            )
        elif role == User.PATIENT:
            phone = request.POST.get("phone")
            Patient.objects.create(
                user=user,
                phone=phone,
            )

        # Аутентифицируемся, чтобы у пользователя был установлен backend
        auth_user = authenticate(request, username=email, password=password)
        if auth_user is not None:
            login(request, auth_user)
        else:
            messages.warning(
                request,
                "Не удалось автоматически войти. Пожалуйста, авторизуйтесь вручную.",
            )

        return redirect("login")


class DashboardView(LoginRequiredMixin, View):
    template_name = "users/dashboard.html"

    def get(self, request):
        return render(request, self.template_name, {"user": request.user})
