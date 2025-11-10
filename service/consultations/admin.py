from django.contrib import admin

from .models import Clinic, Consultation


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ("name", "legal_address", "actual_address")
    search_fields = ("name", "legal_address", "actual_address")
    ordering = ("name",)


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ("clinic", "doctor", "patient", "status", "start_date", "end_date")
    list_filter = ("status", "clinic", "doctor")
    search_fields = ("status", "clinic__name")
    date_hierarchy = "start_date"
    ordering = ("-start_date",)
    raw_id_fields = ("clinic", "doctor", "patient")
