from django.urls import path
from consultations.views import (
    ConsultationListView,
    ConsultationDetailView,
    ConsultationCreateView,
    ConsultationUpdateView,
    ConsultationDeleteView,
    ConsultationRegisterView,
)

app_name = "consultations"

urlpatterns = [
    path("", ConsultationListView.as_view(), name="list"),
    path("<int:pk>/", ConsultationDetailView.as_view(), name="detail"),
    path("create/", ConsultationCreateView.as_view(), name="create"),
    path("<int:pk>/update/", ConsultationUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", ConsultationDeleteView.as_view(), name="delete"),
    path("<int:pk>/register/", ConsultationRegisterView.as_view(), name="register"),
]
