from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('droplocations', views.droplocations, name='droplocations'),
    path('dispatch_addresses', views.dispatch_addresses, name='dispatch_addresses'),
    path('data_form', views.data_form, name='data_form'),
    path('driver_route', views.driver_route, name='driver_route'),
    path('admin_routes', views.admin_routes, name='admin_routes'),
    path('get_waypoint_to_coord', views.get_waypoint_to_coord, name='get_waypoint_to_coord'),
    path('add_data', views.process_data, name='add_data'),
    
]
