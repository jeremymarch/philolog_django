from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="philolog-home"),
    path('query/', views.query, name="philolog-query"),
]
