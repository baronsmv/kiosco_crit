from django import forms


class BuscarPacienteForm(forms.Form):
    carnet = forms.CharField(
        required=True,
        label="Carnet",
        widget=forms.TextInput(
            attrs={"placeholder": "Ingresa el número de carnet", "id": "carnet"}
        ),
    )
    fecha = forms.DateField(
        required=False,
        label="Fecha",
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            attrs={"type": "date", "id": "fecha", "placeholder": "Selecciona una fecha"}
        ),
    )
