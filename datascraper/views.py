from django.shortcuts import render
from django.http import HttpResponse
from .main import main
# Create your views here.

def test(request):
    # return HttpResponse("Hello from VPS!!!!")
    return HttpResponse(main())

