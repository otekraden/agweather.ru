# from django.shortcuts import render
from django.http import HttpResponse

# from .main import main
# from datascraper import models
# from .models import Location, WeatherParameter, ForecastSource, \
#     ForecastTemplate, ArchiveSource, ArchiveTemplate
import os

from dotenv import load_dotenv

from django.core.management.utils import get_random_secret_key


def main(request):

    load_dotenv()

    # a = os.environ["TEST_SECRET"]
    a = os.environ["PROXIES"]

    print(a)

    b = get_random_secret_key()
    print(b)

    return HttpResponse(f"<br>It is main:</br><br><b>{a}</b></br><br>{b}</br>")
