from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from .models import Location

class IndexView(generic.ListView):
    # template_name = "polls/index.html"
    # context_object_name = "latest_question_list"

    def get_queryset(self):
        return Location.objects.all()
