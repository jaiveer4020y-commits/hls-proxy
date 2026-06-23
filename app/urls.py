from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home),
    re_path(r'^movie/\d+/$', views.home),
    re_path(r'^tv/\d+/S\d+/E\d+/$', views.home),
]
