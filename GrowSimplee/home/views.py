from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from rest_framework.decorators import api_view
# Create your views here.

def index(request):
    response = {}
    response['status'] = 'OK'
    response['message'] = 'This is the home page'
    return JsonResponse(response)

def droplocations(request):
    response = {}
    response['status'] = 'OK'
    response['message'] = 'This is the drop locations page'
    return JsonResponse(response)

@csrf_exempt
def dispatch_addresses(request):
    if request.method == "POST":
        print(request.POST)
        pass
    response = {}
    response['status'] = 'OK'
    response['message'] = 'Dispatch Addresses'
    return JsonResponse(response)


def driver_route(request):
    response = {}
    response['status'] = 'OK'
    response['message'] = 'This is the driver route page'
    # For now, hard coded the route
    response['route'] = [[28,77],[30,77],[29,78]]
    return JsonResponse(response)
