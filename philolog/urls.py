from django.conf.urls import handler404
from django.urls import path, re_path
from . import views

urlpatterns = [
    
    path('query/', views.query, name="philolog-query"),
    re_path(r'.*query/.*', views.query, name="philolog-query"),
    re_path(r'.*item/.*', views.get_def, name="philolog-definition"),
    path('', views.home, name="philolog-home"),
    
    #re_path('^((?!item).)*$', views.home, name="philolog-home"),
    #re_path('lsj/', views.home, name="philolog-home"),
    
]

handler404 = views.error404
