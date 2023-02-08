from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('driver_route', views.driver_route, name='driver_route'),
    path('admin_routes', views.admin_routes, name='admin_routes'),
    path('get_waypoint_to_coord', views.get_waypoint_to_coord, name='get_waypoint_to_coord'),
    path('add_data', views.process_data, name='add_data'),
    path('add_pickup_points', views.add_pickup_points, name='add_pickup_points'),
    path('upload/', views.upload, name='upload'),
    path('test_data/', views.test_data, name='test_data'),
    
]
