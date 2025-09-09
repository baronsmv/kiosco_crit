from django import forms


class BuscarIdFechaForm(forms.Form):
    id = forms.CharField(required=True)
    fecha = forms.DateField(
        required=False,
        label="Fecha",
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            attrs={"type": "date", "id": "fecha", "placeholder": "Selecciona una fecha"}
        ),
    )
