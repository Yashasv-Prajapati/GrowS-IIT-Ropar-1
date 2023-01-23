from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

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

