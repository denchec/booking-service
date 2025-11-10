from django import forms

from consultations.models import Consultation
from users.models import Doctor


class ConsultationCreateForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            try:
                doctor = Doctor.objects.get(user=user)
            except Doctor.DoesNotExist:
                doctor = None
            if doctor is not None and "doctor" in self.fields:
                self.fields["doctor"].queryset = Doctor.objects.filter(pk=doctor.pk)
                self.fields["doctor"].initial = doctor

    start_date = forms.DateTimeField(
        label="Начало",
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
            }
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    class Meta:
        model = Consultation
        fields = ["clinic", "doctor", "status", "start_date"]
        labels = {
            "clinic": "Клиника",
            "doctor": "Врач",
            "status": "Статус",
        }
