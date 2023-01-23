from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('droplocations', views.droplocations, name='droplocations'),
]
