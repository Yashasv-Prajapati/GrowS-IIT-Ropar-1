from math import cos, asin, sqrt, pi
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
import pandas as pd
import requests
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import urllib.parse
from dotenv import load_dotenv
import os
import json
import cv2
import numpy as np
from multimethod import multimethod
import datetime
import base64        # To decode base64 images to file
import datetime
import time
import csv


load_dotenv()
API_KEY = os.getenv('API_KEY')
ORS_API_KEY = os.getenv('ORS_API_KEY')

# Data Structures for the routes

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

data = {}
"""
    data['time_windows']
    data['demands']
    data['vehicle_capacities']
    data['distance_matrix']
    data['time_matrix']
    data['num_vehicles']
    data['depot']
"""
# put data from process_data here
data_locations = []
"""
Stores the address, latitude and longitude of different items
here key is the index of the item, i.e. node_index
Format:
[
    {
        'address': 'Address 1',
        'type': 'drop'/'pickup'/'depot',
        'lat': latitude,
        'lon': longitude
        'eod': date/time
        'demand: weight/volume
    },
    ...
]
"""

driver_routes = []
"""
driver_routes stores all the routes for different driver
Format:
[
    [        # Route for driver 0
        [node_index, route_load, time_taken],
        [node_index, route_load, time_taken],
        [node_index, route_load, time_taken],
        [node_index, route_load, time_taken]
        ...
    ],
    [        # Route for driver 1
        [node_index, route_load, time_taken],
        [node_index, route_load, time_taken],
        [node_index, route_load, time_taken],
        [node_index, route_load, time_taken]
        ...
    ],
    ...
]

"""


all_driver_path = []
"""
Format:
[
    [        # Path for driver 0
        [lat0, long0],
        [lat1, long1],
        [lat2, long2],
        ...
    ],
    [        # Path for driver 1
        [latg0, long0],
        [latg1, long1],
        [latg2, long2],
        ...
    ],
    ...
]
"""

all_driver_path_history = []
"""
Format:
Global path history for all the drivers
[   
    [
        [        # Path for driver 0
            [lat0, long0],
            [lat1, long1],
            [lat2, long2],
            ...
        ],
        [        # Path for driver 1
            [latg0, long0],
            [latg1, long1],
            [latg2, long2],
            ...
        ],
        ...
    ],
    [
        [        # Path for driver 0
            [lat0, long0],
            [lat1, long1],
            [lat2, long2],
            ...
        ],
        [        # Path for driver 1
            [latg0, long0],
            [latg1, long1],
            [latg2, long2],
            ...
        ],
        ...
    ]
]
"""

data_location_index = {}
sku_volume_mapping = {}
completed_deliveries = 0

# analytics dictionary
analytics = []
"""
[
    [{
        
        maxTimeTaken:max_time_taken
        minTimeTaken:min_time_taken
        distaceTravelled:dis...
        load:capacity   
    },
    {
        maxTimeTaken:max_time_taken
        minTimeTaken:min_time_taken
        distaceTravelled:dis...
        load:capacity   
    }],
    [{
        maxTimeTaken:max_time_taken
        minTimeTaken:min_time_taken
        distaceTravelled:dis...
        load:capacity    
    }]
]
"""

product_volume_dict = {}
"""
{
    product_id: volume
}
"""

all_dropped_nodes = []

def get_lati_long(query):
    # Using Google Maps API
    with open('data_locations.json', 'r') as f:
        data_locations = json.load(f)

    for i in data_locations:
        if i['address'] == query:
            return i['lat'], i['lon']

    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    response = requests.get(
        base_url, params={'address': query, 'key': API_KEY})
    data = response.json()

    with open('data_locations.json', 'w') as outfile:
        json.dump(data_locations, outfile)
    
    if(data["status"] == "ZERO_RESULTS"):
        return 0,0
    return data['results'][0]['geometry']['location']['lat'], data['results'][0]['geometry']['location']['lng']


def distance(lat1, lon1, lat2, lon2):
    p = pi/180
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * \
        cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return int(12742 * asin(sqrt(a)) * 1000)


def build_time_distance_matrix(locations_list):
    n = len(locations_list)
    distance_matrix = [[-1]*n for i in range(n)]
    locations_lat_long = []
    for i in range(len(locations_list)):
        locations_lat_long.append(
            [locations_list[i]['lat'], locations_list[i]['lon']])
    with open('locations_lat_long.json', 'w') as f:
        json.dump(locations_lat_long, f)
    for i in range(n):
        lat1, lon1 = locations_lat_long[i]
        for j in range(n):
            lat2, lon2 = locations_lat_long[j]
            distance_matrix[i][j] = int(distance(lat1, lon1, lat2, lon2))

    time_matrix = [[-1]*n for i in range(n)]
    for i in range(n):
        for j in range(n):
            time_matrix[i][j] = int(distance_matrix[i][j]*60*60/(40*1000))
    
    data['time_matrix'] = time_matrix
    data['distance_matrix'] = distance_matrix
    return distance_matrix


# def build_time_distance_matrix(locations_list,build):
#     """
#     Builds the distance matrix for the data_locations
#     This will also take care of the api limit
#     """
#     if build is False:
#         with open('time_matrix.json','r') as f:
#             data_store_time_matrix = json.load(f)
#         with open('distance_matrix.json','r') as f:
#             data_store_distance_matrix = json.load(f)

#         data['time_matrix'] = data_store_time_matrix
#         data['distance_matrix'] = data_store_distance_matrix
#         # convert all float values to int
#         for i in range(len(data['time_matrix'])):
#             for j in range(len(data['time_matrix'][i])):
#                 if data['time_matrix'][i][j] is None:
#                     data['time_matrix'][i][j] = 500
#                 data['time_matrix'][i][j] = int(data['time_matrix'][i][j])
#         for i in range(len(data['distance_matrix'])):
#             for j in range(len(data['distance_matrix'][i])):
#                 if data['distance_matrix'][i][j] is None:
#                     data['distance_matrix'][i][j] = 1000
#                 data['distance_matrix'][i][j] = int(data['distance_matrix'][i][j])
#         return data_store_time_matrix, data_store_distance_matrix

#     base_url = "https://api.openrouteservice.org/v2/matrix/driving-car"
#     time_matrix = []
#     distance_matrix = []

#     query_point = 2500//len(locations_list)

#     locations_lat_long = []
#     for i in range(len(locations_list)):
#         locations_lat_long.append([locations_list[i]['lon'],locations_list[i]['lat']])

#     with open('locations_lat_long.json','w') as f:
#         json.dump(locations_lat_long,f)

#     for i in range(0,len(locations_list),query_point):
#         response = requests.post(base_url,json={
#             "locations": locations_lat_long,
#             "metrics": ["duration","distance"],
#             "units": "m",
#             "sources": [j for j in range(i,min(i+query_point,len(locations_list)))],
#         },
#         headers={
#             "Authorization": ORS_API_KEY,
#         })
#         data_res = response.json()
#         for j in range(len(data_res['durations'])):
#             time_matrix.append(data_res['durations'][j])
#             distance_matrix.append(data_res['distances'][j])

#     for i in range(len(time_matrix)):
#         for j in range(len(time_matrix[i])):
#             if time_matrix[i][j] is None:
#                 time_matrix[i][j] = 0
#             time_matrix[i][j] = time_matrix[i][j]
#     for i in range(len(distance_matrix)):
#         for j in range(len(distance_matrix[i])):
#             # TODO: Instead of assigning 0, call google matrix api for this
#             if distance_matrix[i][j] is None:
#                 distance_matrix[i][j] = 0
#             distance_matrix[i][j] = distance_matrix[i][j]
#     data_store_time_matrix = time_matrix
#     data_store_distance_matrix = distance_matrix

#     data['distance_matrix'] = data_store_distance_matrix
#     data['time_matrix'] = data_store_time_matrix
#     with open('time_matrix.json','w') as f:
#         json.dump(time_matrix,f)
#     with open('distance_matrix.json','w') as f:
#         json.dump(distance_matrix,f)

#     return time_matrix, distance_matrix

# Test the build_distance_matrix function
# build_time_distance_matrix([{'lon':9.70093,'lat':48.477473},{'lon':9.207916,'lat':49.153868},{'lon':37.573242,'lat':55.801281},{'lon':115.663757,'lat':38.106467}])


def bag_creation_strategy(bag_num_1, bag_num_2, num_vehicles):
    """
    Returns the bag creation strategy
    bag_num_1 : Number of bags of type 1 (60 X 60 X 100 CMS = 360000 CM3) 
    bag_num_2 : Number of bags of type 2 (80 X 80 X 100 CMS = 640000 CM3)
    """
    capacity_1 = 360000
    capacity_2 = 640000
    # divide the bags of different capacities into vehicles such that volume of each vehicle is almost equal
    # return a list of lists, where each list contains the number of bags of each type in that vehicle

    vehicles_bag_list = [[0, 0, 0] for i in range(num_vehicles)]

    for i in range(num_vehicles):
        vehicles_bag_list[i][0] = bag_num_1//num_vehicles
        vehicles_bag_list[i][1] = bag_num_2//num_vehicles
        vehicles_bag_list[i][2] = bag_num_1//num_vehicles * \
            capacity_1 + bag_num_2//num_vehicles * capacity_2

    vehicles_bag_list.sort(key=lambda x: x[2])

    for i in range(bag_num_1 % num_vehicles):
        vehicles_bag_list[i][0] += 1
        vehicles_bag_list[i][2] += capacity_1

    vehicles_bag_list.sort(key=lambda x: x[2])

    for i in range(bag_num_2 % num_vehicles):
        vehicles_bag_list[i][1] += 1
        vehicles_bag_list[i][2] += capacity_2

    vehicle_demands = [0 for i in range(num_vehicles)]
    for i in range(num_vehicles):
        vehicle_demands[i] = vehicles_bag_list[i][2]

    data['vehicle_capacities'] = vehicle_demands

    return vehicles_bag_list


def index(request):
    response = {}
    response['status'] = 'OK'
    response['message'] = 'This is the home page'
    return JsonResponse(response)


def driver_route(request):
    index = request.GET.get('index')
    index = int(index)
    response = {}
    response['status'] = 'OK'
    response['message'] = 'This is the driver route page'
    if len(all_driver_path) < index:
        response['status'] = 'ERROR'
        response['message'] = 'No route found for this driver'
        return JsonResponse(response)
    response['route'] = all_driver_path[index-1]
    return JsonResponse(response)


def admin_routes(request):
    response = {}
    response['status'] = 'OK'
    response['message'] = 'This is the admin routes page'
    # For now, hard coded the routes
    if driver_routes == []:
        cvrptw_with_dropped_locations()
    response['routes'] = all_driver_path

    return JsonResponse(response)


def convert_edd(edd, date):
    # convert the edd(date)(DD-MM-YYYY) to seconds with respect to given date
    edd = edd.split('-')
    edd = datetime.datetime(int(edd[2]), int(edd[1]), int(edd[0]))
    date = date.split('-')
    date = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))
    seconds = (edd-date).total_seconds()
    return int(seconds)


@csrf_exempt
def process_data(request):

    response = {}
    response['status'] = 'OK'
    response['message'] = 'success'

    global data_locations

    print("Processing Data...")
    # read the data from the file data_locations.json into data_locations
    # Only for local testing
    with open('data_locations.json', 'r') as f:
        data_locations = json.load(f)

    data['time_windows'] = []
    data['depot'] = 0

    # setting data for depot
    if 'depotAdd' in request.POST:
        if len(data_locations)==0 or data_locations[0]['type'] != 'depot':
            data_locations_dict = {}
            data_locations_dict['address'] = request.POST['depotAdd']
            data_locations_dict['type'] = 'depot'
            data_locations_dict['AWB'] = 0
            lat, lon = get_lati_long(data_locations_dict['address'])
            data_locations_dict['lat'] = lat
            data_locations_dict['lon'] = lon
            if lat != 0 or lon != 0:
                data_locations = [data_locations_dict] + data_locations
        elif data_locations[0]['address']!=request.POST['depotAdd']:
            data_locations[0]['address'] = request.POST['depotAdd']
            lat, lon = get_lati_long(data_locations[0]['address'])
            data_locations[0]['lat'] = lat
            data_locations[0]['lon'] = lon
            

    if 'date' in request.POST:
        data['date'] = request.POST['date']

    if 'driverStartWindow' in request.POST:
        data['driverStartWindow'] = request.POST['driverStartWindow']

    if 'driverEndWindow' in request.POST:
        data['driverEndWindow'] = request.POST['driverEndWindow']
    
    for i in range(len(data_locations)):
        data_location_index[data_locations[i]['address']] = i

    # checking dispatchAdd
    if 'dispatchAdd' in request.FILES:
        dispatchAdd = request.FILES['dispatchAdd']
        dispatchAdd_sheet = pd.read_excel(dispatchAdd)
        # setting data for dispatchAdd
        for row in range(dispatchAdd_sheet.shape[0]):
            
            # check if the address is already present in the data_locations
            delivery_date = dispatchAdd_sheet['EDD'][row]
            # Considering six hour shift for the driver
            data['time_windows'].append(
                (0, 21600))
            
            
            # check if the address is already present in the data_location_index as a key
            if dispatchAdd_sheet['address'][row] in data_location_index:
                data_locations[data_location_index[dispatchAdd_sheet['address'][row]]]['AWB']=int(dispatchAdd_sheet['AWB'][row])
                print(data_locations[data_location_index[dispatchAdd_sheet['address'][row]]])
                continue
            data_locations_dict = {}
            data_locations_dict['address'] = dispatchAdd_sheet['address'][row]
            data_locations_dict['type'] = 'drop'
            data_locations_dict['AWB'] = int(dispatchAdd_sheet['AWB'][row])
            lat, lon = get_lati_long(data_locations_dict['address'])
            data_locations_dict['lat'] = lat
            data_locations_dict['lon'] = lon
            if lat != 0 or lon != 0:
                data_locations.append(data_locations_dict)
                data_location_index[data_locations_dict['address']] = len(data_locations)-1
    # checking pickupAdd

    # saving data_locations to data_locations.json
    with open('data_locations.json', 'w') as outfile:
        json.dump(data_locations, outfile)

    # setting data for number of vehicles
    if 'vehicleNum' in request.POST:
        data['num_vehicles'] = int(request.POST['vehicleNum'])

    if 'firstSolutionStrategy' in request.POST:
        data['firstSolutionStrategy'] = request.POST['firstSolutionStrategy']

    if 'metaHeuristic' in request.POST:
        data['metaHeuristic'] = request.POST['metaHeuristic']

    # TODO: Need to set time window for each location
    data['time_windows'] = [[0, 21600]] * len(data_locations)
    data['time_windows'][0] = [0, 4320000]
    
    # setting data for demands
    # TODO: Match the volume of sku and model them as demands
    # Sku number -> Volume, Weight -> Need a file for this
    # Need to add on frontend side
    global sku_volume_mapping
    if 'SKUVolumeMapping' in request.FILES:
        SKUVolumeMapping = request.FILES['SKUVolumeMapping']
        SKUVolumeMapping_sheet = pd.read_excel(SKUVolumeMapping)
        for row in range(SKUVolumeMapping_sheet.shape[0]):
            sku = SKUVolumeMapping_sheet['SKU'][row]
            volume = SKUVolumeMapping_sheet['Volume'][row]
            sku_volume_mapping[sku] = volume
            
    data['demands'] = [10000] * len(data_locations)
    
    for i in range(len(data_locations)):
        if i >= len(dispatchAdd_sheet['product_id']):
            break
        product_id = dispatchAdd_sheet['product_id'][i]
        if data_locations[i]['type'] != 'depot' and product_id in sku_volume_mapping:
            data['demands'][i] = sku_volume_mapping[product_id]

    data['demands'][0] = 0

    # Bag dimensions data
    if 'bagNum1' in request.POST and 'bagNum2' in request.POST and 'num_vehicles' in data:
        bag_creation_strategy(int(request.POST['bagNum1']), int(
            request.POST['bagNum2']), data['num_vehicles'])

    if data_locations is not None:
        print("Building the time-distance matrix")
        build_time_distance_matrix(locations_list=data_locations)

    # replace null values with 0
    # Temporary solution
    # TODO: Compensate with Google API
    for i in range(len(data['time_matrix'])):
        for j in range(len(data['time_matrix'][i])):
            if data['time_matrix'][i][j] is None:
                data['time_matrix'][i][j] = 0

    for i in range(len(data['distance_matrix'])):
        for j in range(len(data['distance_matrix'][i])):
            if data['distance_matrix'][i][j] is None:
                data['distance_matrix'][i][j] = 0

    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)

    print("Done Data Processing")
    # Initial solution called
    cvrptw_with_dropped_locations()

    print("Completed building the solution")
    # For each pickup location, add_pickup_location is called
    # for row in range(pickupAdd_sheet.shape[0]):
    #     add_pickup_location(pickupAdd_sheet['address'][row])

    return JsonResponse(response)


@csrf_exempt
def add_pickup_points(request):
    print("Adding pickup addresses...")
    with open('data_locations.json', 'r') as f:
        data_locations = json.load(f)

    for i in range(len(data_locations)):
        data_location_index[data_locations[i]['address']] = i
    if 'pickupAdd' in request.FILES:
        pickupAdd = request.FILES['pickupAdd']
        pickupAdd_sheet = pd.read_excel(pickupAdd)

        # setting data for pickupAdd
        for row in range(pickupAdd_sheet.shape[0]):
            # check if the address is already present in the data_locations
            
            if pickupAdd_sheet['address'][row] in data_location_index:
                data_locations[data_location_index[pickupAdd_sheet['address'][row]]]['AWB']=int(pickupAdd_sheet['AWB'][row])
                continue
            data_locations_dict = {}
            data_locations_dict['address'] = pickupAdd_sheet['address'][row]
            data_locations_dict['type'] = 'pickup'
            lat, lon = get_lati_long(data_locations_dict['address'])
            data_locations_dict['AWB'] = int(pickupAdd_sheet['AWB'][row])
            data_locations_dict['lat'] = lat
            data_locations_dict['lon'] = lon
            if lat != 0 or lon != 0:
                data_locations.append(data_locations_dict)
                data_location_index[data_locations_dict['address']] = len(data_locations)-1
    
    with open('data_locations.json', 'w') as outfile:
        json.dump(data_locations, outfile)

    if 'time' in request.POST:
        data['time'] = request.POST['time']

    if 'time' in data:
        x = time.strptime(data['time'].split(',')[0],'%H:%M')
        total_seconds = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
        print("Time", data['time'], total_seconds)
        for row in range(pickupAdd_sheet.shape[0]):
            address = pickupAdd_sheet['address'][row]
            time_taken = total_seconds
            product_id = pickupAdd_sheet['product_id'][row]
            volume = 100
            if product_id in sku_volume_mapping:
                volume = sku_volume_mapping[product_id]
            add_pickup_point(address, volume, time_taken)

    print("Pickup Addresses:", pickupAdd)
    
    all_driver_path = driver_paths
    all_driver_path_history.append(all_driver_path)

    driver_path_csv = []
    driver_path_csv.append(["Route", "Latitude", "Longitude", "Address", "AWB"])
    for i in range(len(driver_paths)):
        for j in range(len(driver_paths[i])):
            driver_path_csv.append(["Route "+str(i+1), driver_paths[i][j][0], driver_paths[i][j][1], driver_paths[i][j][2], driver_paths[i][j][3]])
        driver_path_csv.append(["Route "+str(i+1), driver_paths[i][0][0], driver_paths[i][0][1], driver_paths[i][0][2], driver_paths[i][0][3]])
        driver_path_csv.append(["", "", "", "", ""])
    
    with open("driver_paths_after_pickups.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(driver_path_csv)
    print("hi")
    response = {}
    response['status'] = 'OK'
    response['message'] = 'success'
    return JsonResponse(response)

def get_solution(data, manager, routing, assignment, time_callback, distance_callback):
    All_Routes = []

    """Prints assignment on console."""
    print(f'Objective: {assignment.ObjectiveValue()}')
    # Display dropped nodes.
    dropped_nodes = 'Dropped nodes:'
    for node in range(routing.Size()):
        if routing.IsStart(node) or routing.IsEnd(node):
            continue
        if assignment.Value(routing.NextVar(node)) == node:
            dropped_nodes += ' {}'.format(manager.IndexToNode(node))
            all_dropped_nodes.append(manager.IndexToNode(node))
            # print(dropped_nodes)
    print(dropped_nodes)

    # Display routes
    time_dimension = routing.GetDimensionOrDie('Time')
    distance_dimension = routing.GetDimensionOrDie('Distance')
    capacity_dimension = routing.GetDimensionOrDie('Capacity')

    # redundant
    # total_time = 0
    # total_distance = 0
    # total_load=0

    # check if the analytics array is empty of not
    if (len(analytics) != 0):
        analytics.clear()

    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route_load = 0

        analytics_driver_array = []

        routes = []
        
        


        while not routing.IsEnd(index):
            dict_analytics = {}

            time_var = time_dimension.CumulVar(index)
            distance_var = distance_dimension.CumulVar(index)
            capacity_var = capacity_dimension.CumulVar(index)

            minimumTimeTaken = assignment.Min(time_var)
            maximumTimeTaken = assignment.Max(time_var)
            distanceTraveled = assignment.Value(distance_var)
            load = assignment.Value(capacity_var)

            dict_analytics['minimumTimeTaken'] = minimumTimeTaken
            dict_analytics['maximumTimeTaken'] = maximumTimeTaken
            dict_analytics['distanceTraveled'] = distanceTraveled
            dict_analytics['load'] = load

            node_index = manager.IndexToNode(index)
            time_taken = time_callback(index, index+1)
            route_load += data['demands'][node_index]

            route = []
            route.append(node_index)
            route.append(route_load)
            route.append(time_taken)
            routes.append(route)

            # adding analytics dict to anaylytics array
            analytics_driver_array.append(dict_analytics)

            index = assignment.Value(routing.NextVar(index))

        # # last point analytics calculation
        # time_var = time_dimension.CumulVar(index)
        # distance_var = distance_dimension.CumulVar(index)
        # capacity_var = capacity_dimension.CumulVar(index)

        # # Adding last point analytics
        # minimumTimeTaken = assignment.Min(time_var)
        # maximumTimeTaken = assignment.Max(time_var)
        # distanceTraveled = assignment.Value(distance_var)
        # load = assignment.Value(capacity_var)

        # dict_analytics['minimumTimeTaken'] = minimumTimeTaken
        # dict_analytics['maximumTimeTaken'] = maximumTimeTaken
        # dict_analytics['distanceTraveled'] = distanceTraveled
        # dict_analytics['load'] = load

        analytics.append(analytics_driver_array)

        # dumping all info to a json file
        with open('analytics.json', 'w') as outfile:
            json.dump(analytics, outfile)

        # Adding total_distance, total_time and total_load at the end of each analytic
        # redundant code
        # total_time += assignment.Min(time_var)
        # total_distance += assignment.Value(distance_var)
        # total_load += assignment.Value(capacity_var)

        All_Routes.append(routes)

    # Just for checking purposes
    global driver_routes
    driver_routes = All_Routes
    date_driver_ropaths()
    print("Driver Routes: ", driver_routes)
    for i in range(len(driver_routes)):
        print("Driver ",i,": ",len(driver_routes[i]))
    print("Completed the solution")
    return All_Routes

def cvrptw_with_dropped_locations():
    # This function will be used to calculate the routes with dropped locations

    # Instantiate the data problem
    # data = create_data_model()
    # Create the routing index manager

    # convert time_windows array to tuple
    # for i in range(len(data['time_windows'])):
    #     data['time_windows'][i] = tuple(data['time_windows'][i])
    print(len(data['time_matrix']), data['num_vehicles'], data['depot'])

    manager = pywrapcp.RoutingIndexManager(
        len(data['time_matrix']), data['num_vehicles'], data['depot'])

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.

    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        if (data['time_matrix'][from_node][to_node] is None):
            return 0
        return data['time_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Create and register a transit callback.

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    distance_callback_index = routing.RegisterTransitCallback(
        distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        distance_callback_index,
        0,  # no slack
        10000000000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Add Capacity constraint.

    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    def counter_callback(from_index):
        """Returns 1 for any locations except depot."""
        # Convert from routing variable Index to user NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return 1 if (from_node != 0) else 0

    counter_callback_index = routing.RegisterUnaryTransitCallback(counter_callback)

    routing.AddDimensionWithVehicleCapacity(
        counter_callback_index,
        0,  # null slack
        [30]*data['num_vehicles'],  # maximum locations per vehicle
        True,  # start cumul to zero
        'Counter')

    # Allow to drop nodes.
    penalty = 100000
    for node in range(1, len(data['time_matrix'])):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    # Add Time Windows constraint.
    time = 'Time'
    routing.AddDimension(transit_callback_index,
                         30,  # allow waiting time
                         21600,  # maximum time per vehicle
                         False,  # Don't force start cumul to zero.
                         time)
    time_dimension = routing.GetDimensionOrDie(time)

    # Add time window constraints for each location except depot.
    for location_idx, time_window in data['time_windows']:
        if location_idx == 0:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    # search_parameters.first_solution_strategy = (
    #     routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    # search_parameters.local_search_metaheuristic = (
    #     routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    if data['firstSolutionStrategy'] == 'AUTOMATIC':
        search_parameters.first_solution_strategy = ( routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC)
    elif data['firstSolutionStrategy'] == 'SAVINGS':
        search_parameters.first_solution_strategy = ( routing_enums_pb2.FirstSolutionStrategy.SAVINGS)
    elif data['firstSolutionStrategy'] == 'SWEEP':
        search_parameters.first_solution_strategy = ( routing_enums_pb2.FirstSolutionStrategy.SWEEP)
    elif data['firstSolutionStrategy'] == 'PATH_MOST_CONSTRAINED_ARC':
        search_parameters.first_solution_strategy = ( routing_enums_pb2.FirstSolutionStrategy.PATH_MOST_CONSTRAINED_ARC)
    elif data['firstSolutionStrategy'] == 'CHRISTOFIDES':
        search_parameters.first_solution_strategy = ( routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES)
    else:
        search_parameters.first_solution_strategy = ( routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    
    # Setting local search metaheuristic.
    if data['metaHeuristic'] == 'AUTOMATIC':
        search_parameters.local_search_metaheuristic = ( routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC)
    elif data['metaHeuristic'] == 'GREEDY_DESCENT':
        search_parameters.local_search_metaheuristic = ( routing_enums_pb2.LocalSearchMetaheuristic.GREEDY_DESCENT)
    elif data['metaHeuristic'] == 'TABU_SEARCH':
        search_parameters.local_search_metaheuristic = ( routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH)
    elif data['metaHeuristic'] == 'SIMULATED_ANNEALING':
        search_parameters.local_search_metaheuristic = ( routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING)
    elif data['metaHeuristic'] == 'GENERIC_TABU_SEARCH':
        search_parameters.local_search_metaheuristic = ( routing_enums_pb2.LocalSearchMetaheuristic.GENERIC_TABU_SEARCH)
    else:
        search_parameters.local_search_metaheuristic = ( routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)

    search_parameters.time_limit.FromSeconds(10)

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)
    
    print("Before calling get_solution()")
    
    # Print solution on console.
    solution = None
    if assignment:
        solution = get_solution(data, manager, routing,
                                assignment, time_callback, distance_callback)

    driver_path_csv = []
    driver_path_csv.append(["Route", "Latitude", "Longitude", "Address", "AWB"])
    for i in range(len(driver_paths)):
        for j in range(len(driver_paths[i])):
            driver_path_csv.append(["Route "+str(i+1), driver_paths[i][j][0], driver_paths[i][j][1], driver_paths[i][j][2], driver_paths[i][j][3]])
        driver_path_csv.append(["Route "+str(i+1), driver_paths[i][0][0], driver_paths[i][0][1], driver_paths[i][0][2], driver_paths[i][0][3]])
        driver_path_csv.append(["", "", "", "", ""])
    
    with open('driver_paths.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(driver_path_csv)


@csrf_exempt
def get_analytics(request):
    total_distance = 0
    total_time = 0
    driver = 0
    driver_analytics = []
    driver_median = []
    total_ontime_deliveries = 0
    if len(data_locations)==0:
        result = {}
        result['driver'] = 0
        result['median'] = 0
        result['total_distance'] = 0
        result['total_time'] = 0
        result['driver_analytics'] = []
        result['total_ontime_deliveries'] = 0
        result['percentage_ontime_deliveries'] = 0
        result['dropped_nodes'] = []
        return JsonResponse(result)

    for route in driver_routes:
        driver_time = 0
        for path in route:
            driver_time += path[2]

        if len(route) > 1:
            driver+=1
            driver_median.append(len(route)-1)

        print("HHH", driver_time, route)
        total_time += driver_time
        driver_dict = {}
        driver_dict['ontime_deliveries'] = count_ontime_deliveries(route)
        total_ontime_deliveries += driver_dict['ontime_deliveries']
        driver_dict['total_time'] = driver_time
        driver_dict['total_deliveries'] = len(route)
        driver_analytics.append(driver_dict)

    result = {}
    result['median'] = driver_median[int((len(driver_median)-1)/2)]
    result['driver'] = driver
    result['total_distance'] = total_time * 40 / (60*60)
    result['total_time'] = total_time
    result['driver_analytics'] = driver_analytics
    result['total_ontime_deliveries'] = total_ontime_deliveries
    result['percentage_ontime_deliveries'] = (total_ontime_deliveries-len(driver_routes))*100/len(data_locations)
    result['dropped_nodes'] = list(set(all_dropped_nodes[:]))
    return JsonResponse(result)
    
@csrf_exempt
def get_waypoint_to_coord(request):
    # read the query from the request
    query = request.GET.get('query')
    lat, lon = get_lati_long(query)
    response = {}
    response['status'] = 'OK'
    response['message'] = 'Waypoint to coordinates'
    response['lat'] = lat
    response['lon'] = lon
    return JsonResponse(response)


def date_driver_ropaths():
    # Generates the driver_paths list from the driver_routes list
    # Uses data_locations to get the coordinates of the nodes
    global driver_paths
    global data_locations
    if data_locations == []:
        with open('data_locations.json') as f:
            data_locations = json.load(f)
    # print("data_locations: ",data_locations)
    driver_paths = [[] for _ in range(len(driver_routes))]
    for i in range(len(driver_routes)):
        for route in driver_routes[i]:
            node_index = route[0]
            if "AWB" not in data_locations[node_index]:
                data_locations[node_index]["AWB"] = ""
            driver_paths[i].append([
                data_locations[node_index]["lat"],
                data_locations[node_index]["lon"],
                data_locations[node_index]["address"],
                data_locations[node_index]["AWB"],
            ])
    global all_driver_path
    
    all_driver_path = driver_paths
    all_driver_path_history.append(all_driver_path)


# with open('data.json') as f:
#     data = json.load(f)
# with open('data_locations.json') as f:
#     data_locations = json.load(f)
# with open('time_matrix.json') as f:
#     data_store_time_matrix = json.load(f)
# with open('distance_matrix.json') as f:
#     data_store_distance_matrix = json.load(f)
# address1 = "6, Shakambari Nagar, 1st stage, JP Nagar, Bangalore"
# address2 = "1, 24th Main Rd, 1st Phase, Girinagar, KR Layout, Muneshwara T-Block, JP Nagar, Bangalore"
# print(get_distance(address1, address2))


def count_ontime_deliveries(route):
    ontime_deliveries = 0
    total_time = 0
    for node, load, time_taken in route:
        total_time += time_taken
        try:
            expected_time = data['time_windows'][node][1]
        except:
            pass
        
        if total_time <= expected_time:
            ontime_deliveries += 1
    return ontime_deliveries


def add_pickup_point(pickup_address, demand, time_taken):

    print("Adding pickup point...")
    # Finding the free capacity in vehicles after k deliveries

    max_capacity = data['vehicle_capacities']

    min_additional_cost = float('inf')
    min_cost_driver = -1
    min_cost_route = -1
    final_route = []
    with open('data_locations.json', 'r') as f:
        data_locations = json.load(f)
    data_locations_dict = {}
    for i in data_locations:
        data_locations_dict[i['address']] = (i['lat'], i['lon'])

    #TODO: Make this efficient by creating new data_locations_dict
    pickup_index = -1
    for i in range (len(data_locations)):
        if data_locations[i]['address'] == pickup_address:
            pickup_index = i
    
    if pickup_address in data_locations_dict:
        pickup_lat, pickup_lon = data_locations_dict[pickup_address]
    pickup_lat, pickup_lon = get_lati_long(pickup_address)

    for driver_index in range(len(driver_routes)):
        free_capacity = max_capacity[driver_index] - \
            driver_routes[driver_index][-1][1]
        current_time = 0
        
        for route_index in range(len(driver_routes[driver_index])-1):
            free_capacity = max_capacity[driver_index] - \
                driver_routes[driver_index][-1][1]
            free_capacity += driver_routes[driver_index][route_index][1]
            current_time += driver_routes[driver_index][route_index][2]

            if free_capacity < demand or current_time < time_taken:
                continue

            route = driver_routes[driver_index][route_index][:]
            node_index = route[0]

            nxt_route = driver_routes[driver_index][route_index+1][:]
            nxt_node_index = nxt_route[0]

            node_address = data_locations[node_index]['address']
            nxt_node_address = data_locations[nxt_node_index]['address']

            # TODO: Instead of sending request everytime, create distance matrix
            node_lat, node_lon = data_locations_dict[node_address]
            nxt_node_lat, nxt_node_lon = data_locations_dict[nxt_node_address]
            
            additional_cost = distance(node_lat, node_lon, pickup_lat, pickup_lon)
            additional_cost += distance(pickup_lat, pickup_lon, nxt_node_lat, nxt_node_lon)
            additional_cost -= distance(node_lat, node_lon, nxt_node_lat, nxt_node_lon)

            previous_route = [i[:] for i in driver_routes[driver_index]]
            updated_route = [i[:] for i in previous_route]
            
            
            nxt_node = updated_route.pop(route_index+1)
            updated_nxt_node = [nxt_node[0], nxt_node[1],
                                distance(pickup_lat, pickup_lon, nxt_node_lat, nxt_node_lon)]
            updated_route.insert(route_index+1, [pickup_index,
                                -demand, distance(node_lat, node_lon, pickup_lat, pickup_lon)])
            updated_route.insert(route_index+1+1, updated_nxt_node)

            previous_ontime_deliveries = count_ontime_deliveries(previous_route)
            new_ontime_deliveries = count_ontime_deliveries(updated_route)
            difference = previous_ontime_deliveries - new_ontime_deliveries

            additional_cost += difference * 5000
            if min_additional_cost > additional_cost:
                min_additional_cost = additional_cost
                min_cost_driver = driver_index
                min_cost_route = route_index+1
                final_route = updated_route[:]
                final_route[route_index+1][1] += final_route[route_index][1]
                for i in range (route_index+2, len(final_route)):
                    final_route[i][1] -= demand
    
    if min_cost_driver == -1:
        for driver_index in range(len(driver_routes)):
            if len(driver_routes[driver_index]) <= 2:
                min_cost_driver = driver_index
                node_index = driver_routes[-1][0]
                node_address = data_locations[node_index]['address']
                node_lat, node_lon = data_locations_dict[node_address]
                driver_routes[driver_index].append([pickup_index, -demand, distance(node_lat, node_lon, pickup_lat, pickup_lon)])
                break
    else:
        print("Add Pickup Point: ", min_cost_driver, min_cost_route, demand)
        print("Previous:", driver_routes[min_cost_driver][min_cost_route])
        driver_routes[min_cost_driver] = final_route
        
        print("New:", driver_routes[min_cost_driver][min_cost_route])

    

    # Things to do:
    # 1. Add routes_time as initial time for the vehicle... vehicle should start from start node after this time
    # 2. Add routes_load as initial load for the vehicle... vehicle should start from start node with this load
    # 3. Add pickup_point as a new node in the locations_list
    # 4. Construct locations_list and demand with multiple depots (location time written above)
    # 5. To identify whether a location is depot/drop/pickup, you can access the data_locations array

# Things to do in frontend:-
# 1. Manual editing of routes (Within routes and global
# 2. Styling of the pages (Finish touch)

# This function gives the volume of the box using Depth Sensor
# Here img is the colored image with green background, h is the height using depth sensor


def get_volume(img, depth=470, box_height=470, ppm=6.25):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    a_channel = lab[:, :, 1]
    # Here we convert the green background to threshhold
    th = cv2.threshold(a_channel, 127, 255,
                       cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    th = 255-th  # Here we inverse the binary image
    # cv2.imshow("plis",th)
    # We write the lab formatted image in jpeg to read it later
    cv2.imwrite("output.jpeg", th)
    # We read the jpeg formatted image to further image preprocess
    img = cv2.imread(r"output.jpeg")
    img1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Applying Gaussian Blur to remove unneccessary noise like non uniformity at the edges of the object
    img1 = cv2.GaussianBlur(img1, (5, 5), 0)
    # Threshold on the blur image to find the contours
    ret, thresh = cv2.threshold(img1, 100, 255, 0)
    # Finding the contours in the binary image to find the object
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]
    # Forming the minimum area rectangle around the object
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)

    # This will draw the minimum bounding box of the object of interest
    img = cv2.drawContours(img, [box], 0, (0, 255, 255), 2)
    # cv2.imshow("Bounding Rectangles", img[::2, ::2])
    # Getting the minimum area box length in pixels
    l = np.linalg.norm(box[0]-box[1])
    # Getting the minimum area box breadth in pixels
    b = np.linalg.norm(box[1]-box[2])
    h = box_height - depth  # We get the height of the object by subtracting the height of box and the distance of object from the top of box which we find using Ultrasound Depth Sensor
    l_adjusted = (l/ppm) * (depth/box_height)  # Converting the length into mm
    b_adjusted = (b/ppm) * (depth/box_height)  # Converting the breadth into mm
    # Print the adjusted length and breadth of the object
    # print("length", l_adjusted)
    # print("bredth", b_adjusted)
    # adding a factor of 10 mm to cater to the errors as well as add a small margin for efficient packaging
    l_adjusted = l_adjusted+10
    # adding a factor of 10 mm to cater to the errors as well as add a small margin for efficient packaging
    b_adjusted = b_adjusted+10
    h = h+5  # adding a factor of 5 mm to cater to the errors as well as add a small margin for efficient packaging. Errors due to sensor is max 0.9 cm, 0.5cm was calculated based on the samples
    ans = (l_adjusted)*(b_adjusted)*(h)
    ans = int(ans)
    ans /= 1000
    return round(ans)


# with open("data.json", "r") as f:
#     data = json.load(f)
# with open("distance_matrix.json", "r") as f:
#     data['distance_matrix'] = json.load(f)

# distance_matrix = []
# for i in range(len(data['distance_matrix'])):
#     for j in range(len(data['distance_matrix'][i])):
#         distance_matrix.append(data['distance_matrix'][i][j])
# data['distance_matrix'] = distance_matrix

# with open("time_matrix.json", "r") as f:
#     data['time_matrix'] = json.load(f)

# time_matrix = []
# for i in range(len(data['time_matrix'])):
#     for j in range(len(data['time_matrix'][i])):
#         time_matrix.append(data['time_matrix'][i][j])
# data['time_matrix'] = time_matrix

# for i in len(data['time_windows']):
#     data['time_windows'][i]=tuple(data['time_windows'][i])

# cvrptw_with_dropped_locations()
# print(all_driver_path)

@csrf_exempt
def test_data(data):

    with open("data.json", "r") as f:
        data = json.load(f)

    print(len(data['time_windows']))
    print(len(data['demands']))

    with open("distance_matrix.json", "r") as f:
        data['distance_matrix'] = json.load(f)

    distance_matrix = []
    for i in range(len(data['distance_matrix'])):
        for j in range(len(data['distance_matrix'][i])):
            distance_matrix.append(data['distance_matrix'][i][j])

    data['distance_matrix'] = distance_matrix

    with open("time_matrix.json", "r") as f:
        data['time_matrix'] = json.load(f)

    time_matrix = []

    for i in range(len(data['time_matrix'])):
        for j in range(len(data['time_matrix'][i])):
            time_matrix.append(data['time_matrix'][i][j])
    data['time_matrix'] = time_matrix

    for i in len(data['time_windows']):
        data['time_windows'][i] = tuple(data['time_windows'][i])

    cvrptw_with_dropped_locations()

    response = {}
    response['status'] = 'OK'

    return JsonResponse(response)


@csrf_exempt
def upload(request):
    if request.method == 'GET':
        return render(request, 'upload.html')

    if request.method == "POST":
        productID = request.POST['productID']
        height = int(request.POST['productHeight'])
        print(productID, height)
        # print(request.POST['imgBase64'])

        imgdata = base64.b64decode(request.POST['imgBase64'][22:])

        filename = f"images/{productID}_{height}.jpg"
        with open(filename, 'wb') as f:
            f.write(imgdata)
            print("img recieved")
            # =====================================================================
            #                                NOTE
            ppm = 1   # I don't know what this is so I'm just setting it to 1
            try:
                imgVol = get_volume(f, height)
                print(imgVol)
                return HttpResponse(imgVol)                
                
            except Exception as e:
                print("Image upload Error: ", e)
                return HttpResponse("ERROR")

            
            # Since the above function call is not working, I'm commenting the above line
            # imgVol = 50

    