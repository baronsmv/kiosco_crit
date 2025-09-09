from django import forms


class BuscarIdFechaForm(forms.Form):
    id = forms.CharField(required=True)
    fecha = forms.DateField(required=False)
