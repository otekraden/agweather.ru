from django import forms
from .views import ForecastTemplate
from django.core.exceptions import ValidationError

class ConnectSourceForm1(forms.ModelForm):

    class Meta:
        model = ForecastTemplate
        fields = ['location', 'forecast_source']


class ConnectSourceForm2(forms.ModelForm):

    class Meta:
        model = ForecastTemplate
        fields = ['url']

    # def clean_url(self):
    #     data = self.cleaned_data["url"]
    #     # print(self.cleaned_data['forecast_source'])
    #     # self.instance.f
        
    #     if "yandex" not in data:
    #         raise ValidationError("Source url is invalid!")

    #     # Always return a value to use as the new cleaned data, even if
    #     # this method didn't change it.
    #     return data