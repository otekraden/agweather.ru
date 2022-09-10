from django.shortcuts import render

from datascraper.models import Location


def index(request):
    location_list = Location.objects.all()
    context = {"location_list": location_list}
    return render(request, "website/index.html", context)

# # from django.http import HttpResponseRedirect
# # from django.shortcuts import get_object_or_404, render
# # from django.urls import reverse
# from django.views import generic
# from datascraper.models import Location


# class IndexView(generic.ListView):
#     # template_name = "polls/index.html"
#     # context_object_name = "latest_question_list"

#     def get_queryset(self):
#         x = Location.objects.all()
#         print(type(x))
#         return x


# # from django.http import HttpResponse


# # def index(request):
# #     return HttpResponse("Hello, world. You're at the ag index.")