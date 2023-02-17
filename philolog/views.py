from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# from .models import Post

def home(request):
    context = {
        # "posts": Post.objects.all()
    }
    return render(request, "philolog/index.html", context)

def query(request):
    # https://www.w3schools.com/django/ref_lookups_lt.php
    # https://docs.djangoproject.com/en/dev/topics/db/queries/#limiting-querysets
    # Words.objects.filter(unaccented__lt='αβγ')[5:10]
    context = {
        # "posts": Post.objects.all()
    }
    return JsonResponse(request.GET['query'])  # https://stackoverflow.com/questions/2428092/creating-a-json-response-using-django-and-python

def get_def(request):
    context = {
        # "posts": Post.objects.all()
    }
    return HttpResponse("query2 response")
