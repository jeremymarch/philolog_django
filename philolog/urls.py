from django.urls import path

from . import views

urlpatterns = [
    # path('ft', views.fulltext_query, name="philolog-ft"),
    path("range", views.get_words_range, name="philolog-range"),
    path("query", views.get_words, name="philolog-query1"),
    # path('lsj/query', views.get_words, name="philolog-query2"),
    # path('ls/query', views.get_words, name="philolog-query3"),
    # path('slater/query', views.get_words, name="philolog-query4"),
    path("item", views.get_definition, name="philolog-definition1"),
    # path('lsj/item', views.get_definition, name="philolog-definition2"),
    # path('ls/item', views.get_definition, name="philolog-definition3"),
    # path('slater/item', views.get_definition, name="philolog-definition4"),
    path("", views.react_home, name="philolog-home"),
]
