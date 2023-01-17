from django import forms
from datascraper.models import (
    Location,
    ForecastTemplate,
    ForecastSource,
    ArchiveTemplate,
    ArchiveSource, )
from django.core.exceptions import ValidationError
from django.db.models import Count


##########################
# ForecastTemplateWizard #
##########################

class ForecastTemplate1(forms.ModelForm):

    class Meta:
        model = ForecastTemplate
        fields = ['location', 'forecast_source']

    location = forms.ModelChoiceField(
        queryset=Location.objects.annotate(
            num_templates=Count("forecasttemplate")).filter(
            num_templates__lt=ForecastSource.objects.count()).order_by(
                'country', 'name'))


class ForecastTemplate2(forms.ModelForm):

    class Meta:
        model = ForecastTemplate
        fields = ['url']

    def __init__(self, *args, **kwargs):
        self.forecast_source = kwargs.pop("forecast_source")
        super(ForecastTemplate2, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data is not None:
            url = cleaned_data.get("url")

            if not url.startswith(self.forecast_source.url):
                self.add_error('url', ValidationError(
                    "This URL doesn’t belong to the Domain of the Forecast " +
                    "Source you previously selected."),)

        return cleaned_data


class ForecastTemplate3(forms.Form):
    pass


#########################
# ArchiveTemplateWizard #
#########################

class ArchiveTemplate1(forms.ModelForm):

    class Meta:
        model = ArchiveTemplate
        fields = ['location', 'archive_source']

    location = forms.ModelChoiceField(
        queryset=Location.objects.annotate(
            num_templates=Count("archivetemplate")).filter(
            num_templates__lt=ArchiveSource.objects.count()).order_by(
                'country', 'name'))


class ArchiveTemplate2(forms.ModelForm):

    class Meta:
        model = ArchiveTemplate
        fields = ['url']

    def __init__(self, *args, **kwargs):
        self.archive_source = kwargs.pop("archive_source")
        super(ArchiveTemplate2, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data is not None:
            url = cleaned_data.get("url")
            if not url.startswith(self.archive_source.url):
                self.add_error('url', ValidationError(
                    "This URL doesn’t belong to the Domain of the Archive " +
                    "Source you previously selected."),)

        return cleaned_data


class ArchiveTemplate3(forms.Form):
    pass
