from django import forms
from .views import ForecastTemplate


class ConnectSourceForm1(forms.ModelForm):

    class Meta:
        model = ForecastTemplate
        fields = ['location', 'forecast_source']


class ConnectSourceForm2(forms.ModelForm):

    class Meta:
        model = ForecastTemplate
        fields = ['url']
