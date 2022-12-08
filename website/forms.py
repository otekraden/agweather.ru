from django import forms
from datascraper.models import (Location, ForecastTemplate, ForecastSource, )
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Count


class ConnectSourceForm1(forms.Form):

    location_queryset = Location.objects.annotate(
        num_templates=Count("forecasttemplate")).filter(
            num_templates__lt=ForecastSource.objects.count())

    location = forms.ModelChoiceField(queryset=location_queryset)
    forecast_source = forms.ModelChoiceField(
        queryset=ForecastSource.objects.all())


class ConnectSourceForm2(forms.ModelForm):

    class Meta:
        model = ForecastTemplate
        fields = ['url']

    def __init__(self, *args, **kwargs):
        self.forecast_source = kwargs.pop("forecast_source")
        super(ConnectSourceForm2, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data is not None:
            url = cleaned_data.get("url")
            try:
                validate_url = URLValidator()
                validate_url(url)
            except ValidationError:
                self.add_error(
                    'url', ValidationError("This input is not Url."), )
            else:
                if not url.startswith(self.forecast_source.url):
                    self.add_error('url', ValidationError(
                        "This URL doesn’t belong to the Domain of the Source \
                            you previously selected."),)

        return cleaned_data


class ConnectSourceForm3(forms.Form):
    pass
