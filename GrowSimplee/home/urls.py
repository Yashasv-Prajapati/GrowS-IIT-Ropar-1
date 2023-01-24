from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('droplocations', views.droplocations, name='droplocations'),
    path('dispatch_addresses', views.dispatch_addresses, name='dispatch_addresses'),
    path('driver_route', views.driver_route, name='driver_route'),
]
