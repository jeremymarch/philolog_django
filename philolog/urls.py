from django.conf.urls import handler404
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('ft/', views.ft, name="philolog-ft"),
    path('query/', views.query, name="philolog-query1"),
    path('lsj/query/', views.query, name="philolog-query2"),
    path('ls/query/', views.query, name="philolog-query3"),
    path('slater/query/', views.query, name="philolog-query4"),
    path('item/', views.get_def, name="philolog-definition1"),
    path('lsj/item/', views.get_def, name="philolog-definition2"),
    path('ls/item/', views.get_def, name="philolog-definition3"),
    path('slater/item/', views.get_def, name="philolog-definition4"),
    path('', views.home, name="philolog-home"),
    # re_path('lsj/.*', views.home, name="philolog-home"),
    # re_path('ls/.*', views.home, name="philolog-home"),
    # re_path('slater/.*', views.home, name="philolog-home"),
    #re_path('^((?!query).)*$', views.home, name="philolog-home"),
    #re_path('^((?!item).)*$', views.home, name="philolog-home"),
    #re_path('lsj/', views.home, name="philolog-home"),
]

handler404 = views.error404
