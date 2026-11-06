from django import forms

from .models import Persona


class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ["nombre", "cedula", "curso"]
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej. Ana Pérez"}),
            "cedula": forms.TextInput(attrs={"placeholder": "10 dígitos", "inputmode": "numeric"}),
            "curso": forms.TextInput(attrs={"placeholder": "Ej. Software 5to A"}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data["cedula"].strip()
        if not cedula.isdigit() or len(cedula) != 10:
            raise forms.ValidationError("La cédula debe tener 10 dígitos.")
        return cedula

    def clean_nombre(self):
        return " ".join(self.cleaned_data["nombre"].split()).title()


class FiltroHistorialForm(forms.Form):
    desde = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    persona = forms.ModelChoiceField(queryset=Persona.objects.all(), required=False, empty_label="Todas")
