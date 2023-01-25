from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
import pandas as pd
import requests
from geopy.geocoders import Nominatim
import urllib.parse

# Create your views here.
# Data Structures for the routes
# Dictionary for SKUs and their weights and voulumes
# sku = {
#     'sku1': {
#         'weight': 10,
#         'volume': 10
#     },
#     'sku2': {
#         'weight': 10,
#         'volume': 10
#     }
# }
# Dictionary for the drop locations, with sku, eod, and the coordinates
# drop_locations = {
#     'drop1': {
#         'sku': 'sku1',
#         'eod': 10,
#         'coord': [28,77]
#     },
#     'drop2': {
#         'sku': 'sku2',
#         'eod': 10,
#         'coord': [28,77]
#     }
# }
# Matrix for the distances and time between the drop locations
# In this distance matrix, column 1 is drop1, column 2 is drop2, and column 3 is drop3
# distance_matrix = [
#     [0, 10, 20],
#     [10, 0, 10],
#     [20, 10, 0]
# ]
# time_matrix = [
#     [0, 10, 20],
#     [10, 0, 10],
#     [20, 10, 0]
# ]
# Dictionary for the driver routes or simply a array of arrays of drop locations

# Data needed to be passed : ‘Demands’, ‘Time windows’, ‘Vehicle capacities’, ‘Distance matrix’ and ‘Time matrix’


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

def get_distance(addresses):
    for i in range (len(addresses)):
        addresses[i] = addresses[i].strip()
    address = 'Shivaji Nagar, Bangalore, KA 560001'
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
    response = requests.get(url).json()
    print(response[0]["lat"])
    print(response[0]["lon"])

    # print("HHH", addresses[0])
    # locator = Nominatim(user_agent="geoapiExercises")
    # print(locator)
    # location = locator.geocode("1600 Amphitheatre Parkway, Mountain View, CA")
    # print(location)



    pass
@csrf_exempt
def dispatch_addresses(request):
    if request.method == "POST":
        print("HHH", request.POST)
        print(request.FILES)
        file = request.FILES['file']
        df = pd.read_excel(file)
        # print(df)
        addresses = df['address'].tolist()
        get_distance(addresses)
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

def admin_routes(request):
    response = {}
    response['status'] = 'OK'
    response['message'] = 'This is the admin routes page'
    # For now, hard coded the routes
    response['routes'] = [[[28,77],[30,77]],[[28,78],[30,78],[32,78]]]
    return JsonResponse(response)

def waypoint_to_coord(query):
    # Need a api that accuractely converts a waypoint to coordinates, for now using positionstack, later will replace this with a better api
    # Fetch from the api
    api = f'http://api.positionstack.com/v1/forward?access_key=318745546a93fdc9015a27db5a3fe5bc&query=${query}'
    response = requests.get(api)
    data = response.json()
    print(data)
    return data['data'][0]['latitude'], data['data'][0]['longitude']

@csrf_exempt
def get_waypoint_to_coord(request):
    # read the query from the request
    query = request.GET.get('query')
    print("query",query)
    lat, lon = waypoint_to_coord(query)
    print(lat,lon)
    response = {}
    response['status'] = 'OK'
    response['message'] = 'Waypoint to coordinates'
    response['lat'] = lat
    response['lon'] = lon
    return JsonResponse(response)