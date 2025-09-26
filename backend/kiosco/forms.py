from django import forms


class BuscarFechaForm(forms.Form):
    fecha = forms.DateField(required=True)


class BuscarIdFechaForm(forms.Form):
    id = forms.CharField(required=True)
    fecha = forms.DateField(required=False)
