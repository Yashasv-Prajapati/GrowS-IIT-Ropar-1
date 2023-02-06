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

load_dotenv()
API_KEY = os.getenv('API_KEY')
ORS_API_KEY = os.getenv('ORS_API_KEY')
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

data_store_time_matrix = []
data_store_distance_matrix = []
completed_deliveries = 0

# analytics dictionary
analytics = []
"""
[
    {
        
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
    },
    {
        maxTimeTaken:max_time_taken
        minTimeTaken:min_time_taken
        distaceTravelled:dis...
        load:capacity    
    }
]
"""




def get_lati_long(query):
    # Using Google Maps API
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    response = requests.get(base_url,params={'address':query,'key':API_KEY})
    data = response.json()
    # print(data)
    return data['results'][0]['geometry']['location']['lat'], data['results'][0]['geometry']['location']['lng']


def build_time_distance_matrix(locations_list,build):
    """
    Builds the distance matrix for the data_locations
    This will also take care of the api limit
    """
    if build is False:
        with open('time_matrix.json','r') as f:
            data_store_time_matrix = json.load(f)
        with open('distance_matrix.json','r') as f:
            data_store_distance_matrix = json.load(f)

        data['time_matrix'] = data_store_time_matrix
        data['distance_matrix'] = data_store_distance_matrix
        return data_store_time_matrix, data_store_distance_matrix

    print("Hi")
    base_url = "https://api.openrouteservice.org/v2/matrix/driving-car"
    time_matrix = []
    distance_matrix = []

    query_point = 2500//len(locations_list)

    locations_lat_long = []
    for i in range(len(locations_list)):
        locations_lat_long.append([locations_list[i]['lon'],locations_list[i]['lat']])

    with open('locations_lat_long.json','w') as f:
        json.dump(locations_lat_long,f)

    for i in range(0,len(locations_list),query_point):
        response = requests.post(base_url,json={
            "locations": locations_lat_long,
            "metrics": ["duration","distance"],
            "units": "m",
            "sources": [j for j in range(i,min(i+query_point,len(locations_list)))],
        },
        headers={
            "Authorization": ORS_API_KEY,
        })
        data_res = response.json()
        print(data_res)
        for j in range(len(data_res['durations'])):
            time_matrix.append(data_res['durations'][j])
            distance_matrix.append(data_res['distances'][j])

    data_store_time_matrix = time_matrix
    data_store_distance_matrix = distance_matrix
    
    data['distance_matrix'] = data_store_distance_matrix
    data['time_matrix'] = data_store_time_matrix
    with open('time_matrix.json','w') as f:
        json.dump(time_matrix,f)
    with open('distance_matrix.json','w') as f:
        json.dump(distance_matrix,f)
    
    return time_matrix, distance_matrix

# Test the build_distance_matrix function
# build_time_distance_matrix([{'lon':9.70093,'lat':48.477473},{'lon':9.207916,'lat':49.153868},{'lon':37.573242,'lat':55.801281},{'lon':115.663757,'lat':38.106467}])

def bag_creation_strategy(bag_num_1,bag_num_2,num_vehicles):
    """
    Returns the bag creation strategy
    bag_num_1 : Number of bags of type 1 (60 X 60 X 100 CMS = 36000 CM3) 
    bag_num_2 : Number of bags of type 2 (80 X 80 X 100 CMS = 64000 CM3)
    """
    capacity_1 = 36000
    capacity_2 = 64000
    # divide the bags of different capacities into vehicles such that volume of each vehicle is almost equal
    # return a list of lists, where each list contains the number of bags of each type in that vehicle

    vehicles_bag_list = [[0,0,0] for i in range(num_vehicles)]

    for i in range(num_vehicles):
        vehicles_bag_list[i][0] = bag_num_1//num_vehicles
        vehicles_bag_list[i][1] = bag_num_2//num_vehicles
        vehicles_bag_list[i][2] = bag_num_1//num_vehicles * capacity_1 + bag_num_2//num_vehicles * capacity_2

    vehicles_bag_list.sort(key = lambda x: x[2])

    for i in range(bag_num_1%num_vehicles):
        vehicles_bag_list[i][0] += 1
        vehicles_bag_list[i][2] += capacity_1

    vehicles_bag_list.sort(key = lambda x: x[2])

    for i in range(bag_num_2%num_vehicles):
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

def droplocations(request):
    response = {}
    response['status'] = 'OK'
    response['message'] = 'This is the drop locations page'
    return JsonResponse(response)


    # address = 'Shivaji Nagar, Bangalore, KA 560001'
    # url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
    # response = requests.get(url).json()
    # print(response[0]["lat"])
    # print(response[0]["lon"])
        
    # print("HHH", addresses[0])
    # locator = Nominatim(user_agent="geoapiExercises")
    # print(locator)
    # location = locator.geocode("1600 Amphitheatre Parkway, Mountain View, CA")
    # print(location)

@csrf_exempt
def dispatch_addresses(request):
    if request.method == "POST":
        print("HHH", request.POST)
        print(request.FILES)
        file = request.FILES['file']
        df = pd.read_excel(file)
        # print(df)
        addresses = df['address'].tolist()
        get_lati_long(addresses)
        pass
    response = {}   
    response['status'] = 'OK'
    response['message'] = 'Dispatch Addresses'
    return JsonResponse(response)

@csrf_exempt
def data_form(request):
    print(request.POST)
    print(request.FILES)
    number_of_vehicles = int(request.POST['number_of_vehicles'][0])
    vehicle_capacity = []
    for i in range (number_of_vehicles):
        current_capacity = int(request.POST['vehicle_'+str(i)+'_capacity'])
        vehicle_capacity.append(current_capacity)
    dispatch_addresses = request.FILES['dispatch_addresses']
    dispatch_df = pd.read_excel(dispatch_addresses)
    pickup_addresses = request.FILES['pickup_addresses']
    pickup_df = pd.read_excel(pickup_addresses)
    
    print(number_of_vehicles)
    print(vehicle_capacity)
    print(dispatch_df)
    print(pickup_df)

    data['number_of_vehicles'] = number_of_vehicles
    data['vehicle_capacity'] = vehicle_capacity
    response = {}
    response['status'] = 'OK'
    response['message'] = 'Data added successfully'
    return JsonResponse(response)

def driver_route(request):
    index = request.GET.get('index')
    response = {}
    response['status'] = 'OK'
    response['message'] = 'This is the driver route page'
    response['route'] = driver_routes[index]
    return JsonResponse(response)

def admin_routes(request):
    response = {}
    response['status'] = 'OK'
    response['message'] = 'This is the admin routes page'
    # For now, hard coded the routes
    # if driver_routes == []:
    #     cvrptw_with_dropped_locations()
    response['routes'] = driver_routes
    return JsonResponse(response)

@csrf_exempt
def process_data(request):
    
    response = {}
    response['status']='OK'
    response['message']='success'

    print("hi")

    # read the data from the file data_locations.json into data_locations
    with open('data_locations.json', 'r') as f:
        data_locations = json.load(f)

    # print(request.FILES['dispatchAdd'])
    # print(request.FILES)

    # checking dispatchAdd
    if 'dispatchAdd' in request.FILES:
        dispatchAdd = request.FILES['dispatchAdd']
        dispatchAdd_sheet = pd.read_excel(dispatchAdd)

        # setting data for dispatchAdd
        for row in range(dispatchAdd_sheet.shape[0]):
            # check if the address is already present in the data_locations
            if dispatchAdd_sheet['address'][row] in [data_locations_dict['address'] for data_locations_dict in data_locations]:
                continue
            data_locations_dict = {}
            data_locations_dict['address']= dispatchAdd_sheet['address'][row]
            data_locations_dict['type']='drop'
            lat, lon = get_lati_long(data_locations_dict['address'])
            data_locations_dict['lat'] = lat
            data_locations_dict['lon'] = lon
            data_locations.append(data_locations_dict)
    
    # checking pickupAdd
    if 'pickupAdd' in request.FILES:
        pickupAdd = request.FILES['pickupAdd']
        pickupAdd_sheet = pd.read_excel(pickupAdd)

        # setting data for pickupAdd
        for row in range(pickupAdd_sheet.shape[0]):
            # check if the address is already present in the data_locations
            if pickupAdd_sheet['address'][row] in [data_locations_dict['address'] for data_locations_dict in data_locations]:
                continue
            data_locations_dict = {}
            data_locations_dict['address']= pickupAdd_sheet['address'][row]
            data_locations_dict['type']='pickup'
            lat, lon = get_lati_long(data_locations_dict['address'])
            data_locations_dict['lat'] = lat
            data_locations_dict['lon'] = lon
            data_locations.append(data_locations_dict)

    # saving data_locations to data_locations.json
    with open('data_locations.json', 'w') as outfile:
        json.dump(data_locations, outfile)

    # setting data for number of vehicles
    if 'vehicleNum' in request.POST:
        data['num_vehicles'] = int(request.POST['vehicleNum'])

    # setting data for time window
    # TODO: Need to set time window for each location
    data['time_windows'] = [[0, 43200]] * len(data_locations)

    # setting data for demands
    # TODO: Match the volume of sku and model them as demands
    # Sku number -> Volume, Weight -> Need a file for this
    # Need to add on frontend side
    data['demands'] = [100] * len(data_locations)
    data['demands'][0] = 0

    # Bag dimensions data
    # TODO: Bag dimensions data -> Vehicle capacities thing
    if 'bagNum1' in request.POST and 'bagNum2' in request.POST and 'num_vehicles' in data:
        bag_creation_strategy(int(request.POST['bagNum1']),int(request.POST['bagNum2']),data['num_vehicles'])

    if data_locations is not None:
        print("Building the time-distance matrix")
        build_time_distance_matrix(locations_list=data_locations,build = False)

    # TODO: Need to set the depot location
    # setting data for depot
    data['depot'] = 0

    # replace null values with 0
    # Temporary solution
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


def create_data_model():
    """Stores the data for the problem."""

    # In this we need to create time matrix using the DISTANCE API
    # Time window, vehicle capacity, demands, num_vehicles will be provided in the data
    data['time_matrix'] = [
                [0, 6, 9, 8, 7, 3, 6, 2, 3, 2, 6, 6, 4, 4, 5, 9, 7],
                [6, 0, 8, 3, 2, 6, 8, 4, 8, 8, 13, 7, 5, 8, 12, 10, 14],
                [9, 8, 0, 11, 10, 6, 3, 9, 5, 8, 4, 15, 14, 13, 9, 18, 9],
                [8, 3, 11, 0, 1, 7, 10, 6, 10, 10, 14, 6, 7, 9, 14, 6, 16],
                [7, 2, 10, 1, 0, 6, 9, 4, 8, 9, 13, 4, 6, 8, 12, 8, 14],
                [3, 6, 6, 7, 6, 0, 2, 3, 2, 2, 7, 9, 7, 7, 6, 12, 8],
                [6, 8, 3, 10, 9, 2, 0, 6, 2, 5, 4, 12, 10, 10, 6, 15, 5],
                [2, 4, 9, 6, 4, 3, 6, 0, 4, 4, 8, 5, 4, 3, 7, 8, 10],
                [3, 8, 5, 10, 8, 2, 2, 4, 0, 3, 4, 9, 8, 7, 3, 13, 6],
                [2, 8, 8, 10, 9, 2, 5, 4, 3, 0, 4, 6, 5, 4, 3, 9, 5],
                [6, 13, 4, 14, 13, 7, 4, 8, 4, 4, 0, 10, 9, 8, 4, 13, 4],
                [6, 7, 15, 6, 4, 9, 12, 5, 9, 6, 10, 0, 1, 3, 7, 3, 10],
                [4, 5, 14, 7, 6, 7, 10, 4, 8, 5, 9, 1, 0, 2, 6, 4, 8],
                [4, 8, 13, 9, 8, 7, 10, 3, 7, 4, 8, 3, 2, 0, 4, 5, 6],
                [5, 12, 9, 14, 12, 6, 6, 7, 3, 3, 4, 7, 6, 4, 0, 9, 2],
                [9, 10, 18, 6, 8, 12, 15, 8, 13, 9, 13, 3, 4, 5, 9, 0, 9],
                [7, 14, 9, 16, 14, 8, 5, 10, 6, 5, 4, 10, 8, 6, 2, 9, 0],
            ]
    # According to our problem, the first parameter will be zero only
    data['time_windows'] = [
                (0, 60),  # depot
                (0, 30),  # 1
                (0, 40),  # 2
                (0, 50),  # 3
                (0, 30),  # 4
                (0, 40),  # 5
                (0, 60),  # 6
                (0, 50),  # 7
                (0, 50),  # 8
                (0, 30),  # 9
                (0, 40),  # 10
                (0, 15),  # 11
                (0, 5),  # 12
                (0, 10),  # 13
                (0, 8),  # 14
                (0, 15),  # 15
                (0, 15),  # 16
              ]
    data['demands'] = [0, 1, 1, 2, 4, 2, 4, 8, 3, 1, 2, 1, 2, 4, 4, 5, 5]
    data['vehicle_capacities'] = [15, 15]
    data['num_vehicles'] = 2
    data['depot'] = 0
    return data

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
    if(len(analytics) !=0):
        analytics.clear()


    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route_load = 0

        routes = []
        print("while not routing")

        while not routing.IsEnd(index):
            dict_analytics = {}
            print(index)

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
            print(dict_analytics)

            node_index = manager.IndexToNode(index)
            time_taken = time_callback(index, index+1)
            route_load += data['demands'][node_index]
            
            route = []
            route.append(node_index)
            route.append(route_load)
            route.append(time_taken)
            routes.append(route)
        
            # adding analytics dict to anaylytics array
            analytics.append(dict_analytics)

            index = assignment.Value(routing.NextVar(index))

        # last point analytics calculation
        time_var = time_dimension.CumulVar(index)
        distance_var = distance_dimension.CumulVar(index)
        capacity_var = capacity_dimension.CumulVar(index)
        
        # Adding last point analytics
        minimumTimeTaken = assignment.Min(time_var)
        maximumTimeTaken = assignment.Max(time_var)
        distanceTraveled = assignment.Value(distance_var)
        load = assignment.Value(capacity_var)

        dict_analytics['minimumTimeTaken'] = minimumTimeTaken
        dict_analytics['maximumTimeTaken'] = maximumTimeTaken
        dict_analytics['distanceTraveled'] = distanceTraveled
        dict_analytics['load'] = load

        analytics.append(dict_analytics)

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
    driver_routes = All_Routes
    date_driver_ropaths()
    print(driver_routes)
    print(all_driver_path)
    return All_Routes

def cvrptw_with_dropped_locations():
    # This function will be used to calculate the routes with dropped locations
    
    # Instantiate the data problem
    # data = create_data_model()
    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),data['num_vehicles'], data['depot'])
    
    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)



    # Create and register a transit callback.
    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        if(data['time_matrix'][from_node][to_node] is None):
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

    distance_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        distance_callback_index,
        0,  # no slack
        10_000,  # vehicle maximum travel distance
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

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')
    

    # Allow to drop nodes.
    penalty = 1000
    for node in range(1, len(data['time_matrix'])):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    
    # Add Time Windows constraint.
    time = 'Time'
    routing.AddDimension(transit_callback_index,
        30,  # allow waiting time
        30,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        time)
    routing.AddDimension(transit_callback_index,
        30,  # allow waiting time
        30,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        time)
    time_dimension = routing.GetDimensionOrDie(time)
    
    
    # Add time window constraints for each location except depot.
    for location_idx, time_window in data['time_windows']:
        # print(time_window)
        if location_idx == 0:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])


    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(60)

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    solution = None
    if assignment:
        solution = get_solution(data, manager, routing, assignment, time_callback, distance_callback)

@csrf_exempt
def get_waypoint_to_coord(request):
    # read the query from the request
    query = request.GET.get('query')
    print("query",query)
    lat, lon = get_lati_long(query)
    #print(lat,lon)
    response = {}
    response['status'] = 'OK'
    response['message'] = 'Waypoint to coordinates'
    response['lat'] = lat
    response['lon'] = lon
    return JsonResponse(response)

def find_kth_delivery_item(k):
    # This function finds information of the kth delivery item being delivered
    # It returns a list of the following format:
    # [driver_index, node_index, route_load, total_time]
    # Here total_time is the time taken to reach the kth delivery item from the depot


    # Creating a list of tuple of all items being delivered and then finally we will sort it to find kth item
    # The tuple will be of the format (driver_index, node_index, route_load, total_time)
    all_items = []
    driver_index = 0
    for routes in driver_routes:
        time = 0
        for route in routes:
            node_index = route[0]
            route_load = route[1]
            time_taken = route[2]
            time += time_taken
            all_items.append((driver_index, node_index, route_load, time))
        driver_index += 1
    
    # Sorting the list of tuples
    all_items.sort(key = lambda x: x[3])

    # Returning the kth item
    try:
        return all_items[k]
    except IndexError:
        print("IndexError in find_kth_delivery_item function: k is greater than the number of items being delivered")


def update_driver_routes(k):
    # This function updates the driver_routes list after the kth delivery item has been delivered
    # All the items before the kth item will be removed from the list
    # kth item will also be removed from the driver_routes list

    # Creating a list of tuple of all items being delivered and then finally we will sort it to find kth item
    # The tuple will be of the format (total_time, driver_index, node_index, route_load, time_taken)
    all_items = []
    driver_index = 0
    for routes in driver_routes:
        time = 0
        for route in routes:
            node_index = route[0]
            route_load = route[1]
            time_taken = route[2]
            time += time_taken
            all_items.append((time, driver_index, node_index, route_load, time_taken))
        driver_index += 1
    
    # Sorting the list of tuples
    all_items.sort(key = lambda x: x[0])

    # Creating updated driver_routes list
    updated_driver_routes = [[] for _ in range(len(driver_routes))]
    driver_start_time = [-1]*len(driver_routes)
    for i in range(k, len(all_items)):
        driver_index = all_items[i][1]
        updated_driver_routes[driver_index].append(all_items[i][2:])
        if driver_start_time[driver_index]==-1:
            driver_start_time[driver_index] = time
    
    # Updating the driver_routes list
    driver_routes = updated_driver_routes

def date_driver_ropaths():
    # Generates the driver_paths list from the driver_routes list
    # Uses data_locations to get the coordinates of the nodes
    global driver_paths
    driver_paths = [[] for _ in range(len(driver_routes))]
    for i in range(len(driver_routes)):
        for route in driver_routes[i]:
            node_index = route[0]
            driver_paths[i].append([
                data_locations[node_index]["lat"],
                data_locations[node_index]["lon"]
            ])
    

def get_time_taken(k):
    # This function returns the time taken to complete k deliveries

    # Creating a list of tuple of all items being delivered and then finally we will sort it to find kth item
    # The tuple will be of the format (total_time, driver_index, node_index, route_load, time_taken)
    all_items = []
    driver_index = 0
    for routes in driver_routes:
        time = 0
        for route in routes:
            node_index = route[0]
            route_load = route[1]
            time_taken = route[2]
            time += time_taken
            all_items.append((time, driver_index, node_index, route_load, time_taken))
        driver_index += 1

    # Sorting the list of tuples
    all_items.sort(key = lambda x: x[0])

    if k>len(all_items):
        return float('inf')
    else:
        return all_items[k-1][0]

# ============================== MERGE CONFLICT ================================
'''
        routes_time.append(routes[0][2]-last_time)
        routes_load.append(routes[0][1])

    # This will update the driver_routes list
    # These updated paths will serve as initial paths for the new pickup point
    all_driver_path_history.append(all_driver_path)
    update_driver_routes(additional_deliveries)

    # This will update the driver_paths list
    date_driver_ropaths()

    # Build a distance matrix for this pickup point
    pickup_point = get_lati_long(address)
    lat = pickup_point[0]
    lon = pickup_point[1]
    pickup_point = [lat, lon]

    # How parameters will be changed that will have to seen
    # Updated routes will be used as initial routes
    # 1.
    # Updated route start point will be used as initial route start point... This have to be set starting point for vehicle
    # But vehicle can be between two nodes... how to manage that thing
    # 2.
    # Capacity of the vehicle will be cumulative weight till that point
    # That will also have to be set as initial capacity of the vehicle
    
    locations_list = []
    # For each delivery item, we will have to add duplicate depot and delivery point with demands [-x,x]
    # For each pickup item, we will have to add pickup point and duplicate depot with demands [x,-x]
    # [depot, pickup_point, duplicate_depot...,  duplicate_depot, delivery_point, duplicate_depot, delivery_point...]
    build_locations_list()

    data['depot'] = 0
    data['time_matrix'] = create_distance_matrix(locations_list)

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),data['num_vehicles'], data['depot'])

'''
# =========================================================

#TODO
def get_distance(address1, address2):
    # check if address1 and address2 are in the data_locations list or not, if they are, find their index and return the distance and time
    # if they are not, then find the distance and time using google maps api and return it
    node_index1 = -1
    node_index2 = -1
    option = 1
    address_list = [data_locations_dict['address'] for data_locations_dict in data_locations]
    if address1 in address_list:
        node_index1 = address_list.index(address1)
    if address2 in address_list:
        node_index2 = address_list.index(address2)
    if node_index1!=-1 and node_index2!=-1 and option == 1:
        return (data_store_distance_matrix[0][node_index1][node_index2], data_store_time_matrix[0][node_index1][node_index2])
    else:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="+address1+"&destinations="+address2+"&key=AIzaSyDAHiXvLdpAhTMfnWbQgL2cigqtsFkfuFQ"
        response = requests.request("GET", url)
        data = response.json()
        distance = data['rows'][0]['elements'][0]['distance']['text']
        duration = data['rows'][0]['elements'][0]['duration']['text']
        return (distance, duration)

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
        expected_time = data['time_windows'][node][1]
        if total_time <= expected_time:
            ontime_deliveries+=1
    return ontime_deliveries


def add_pickup_point(pickup_address, demand, k):
    time_taken = get_time_taken(k)

    # Finding the free capacity in vehicles after k deliveries
    max_capacity = data['vehicle_capacities']

    min_additional_cost = float('inf')
    min_cost_driver = -1
    min_cost_route = -1

    for driver_index in range (len(driver_routes)):
        free_capacity = 0
        current_time = 0
        for route_index in range (len(driver_routes[driver_index])-1):
            free_capacity += driver_routes[driver_index][route_index][1]
            current_time += driver_routes[driver_index][route_index][2]
            
            if free_capacity < demand or current_time < time_taken:
                continue

            route = driver_routes[driver_index][route_index]
            node_index = route[0]

            nxt_route = driver_routes[driver_index][route_index+1]
            nxt_node_index = nxt_route[0]

            node_address = data['node_addresses'][node_index]
            nxt_node_address = data['node_addresses'][nxt_node_index]
            
            # TODO: Instead of sending request everytime, create distance matrix
            additional_cost = get_distance(node_address, pickup_address)
            additional_cost += get_distance(pickup_address, nxt_node_address)
            additional_cost -= get_distance(node_address, nxt_node_address)
            
            if min_additional_cost > additional_cost:
                min_additional_cost = additional_cost
                min_cost_driver = driver_index
                min_cost_route = route_index + 1
    
    previous_route = driver_routes[min_cost_driver]
    updated_route = previous_route[:]

    nxt_node = updated_route.pop(min_cost_route)
    updated_nxt_node = (nxt_node[0], nxt_node[1], get_distance(nxt_node[0], pickup_address))
    updated_route.insert(min_cost_route, (pickup_address, -demand, get_distance(node_address, pickup_address)))
    updated_route.insert(min_cost_route+1, updated_nxt_node)

    previous_ontime_deliveries = count_ontime_deliveries(previous_route)
    new_ontime_deliveries = count_ontime_deliveries(updated_route)
    difference = previous_ontime_deliveries - new_ontime_deliveries

    # TODO: Modify penalty logic
    if difference>1:
        # Dont add pickup node
        return
    else:
        good = 5
        bad = additional_cost + 3*difference
        delta = good - bad
        if delta >= 0:
            driver_routes[min_cost_driver] = updated_route
        else:
            # Dont add pickup node
            pass
        return

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
@multimethod
def get_volume(img,h:int,ppm):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    a_channel = lab[:,:,1]
    th = cv2.threshold(a_channel,127,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    th = 255-th
    # cv2.imshow("plis",th)
    cv2.imwrite("output.jpeg",th)
    img = cv2.imread("output.jpeg")
    img1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img1= cv2.GaussianBlur(img1,(5,5),0)
    ret,thresh = cv2.threshold(img1,100,255,0)
    contours,_ = cv2.findContours(thresh, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)

    # draw minimum area rectangle (rotated rectangle)
    # img = cv2.drawContours(img,[box],0,(0,255,255),2)
    # cv2.imshow("Bounding Rectangles", img)
    l=np.linalg.norm(box[0]-box[1])
    b=np.linalg.norm(box[1]-box[2])

    return l*b*h/(ppm*ppm*ppm)

# This function gives us the volume if we have two photos shot from perpendicular field of view
@multimethod
def get_volume(img_top,img_ver,ppm):
    img = img_top
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    a_channel = lab[:,:,1]
    th = cv2.threshold(a_channel,127,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    masked = cv2.bitwise_and(img, img, mask = th)
    th = 255-th
    # cv2.imshow("plis",th)
    cv2.imwrite("output.jpeg",th)
    img = cv2.imread("output.jpeg")
    img1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img1= cv2.GaussianBlur(img1,(5,5),0)
    ret,thresh = cv2.threshold(img1,100,255,0)
    contours,_ = cv2.findContours(thresh, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)

    # draw minimum area rectangle (rotated rectangle)
    # img = cv2.drawContours(img,[box],0,(0,255,255),2)
    # cv2.imshow("Bounding Rectangles", img)
    l=np.linalg.norm(box[0]-box[1])
    b=np.linalg.norm(box[1]-box[2])


    img=img_ver
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    a_channel = lab[:,:,1]
    th = cv2.threshold(a_channel,127,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    th = 255-th
    # cv2.imshow("plis",th)
    cv2.imwrite("output.jpeg",th)
    img = cv2.imread("output.jpeg")
    img1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img1= cv2.GaussianBlur(img1,(5,5),2)
    ret,thresh = cv2.threshold(img1,100,255,0)
    contours,_ = cv2.findContours(thresh, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]
    h = cv2.boundingRect(cnt)[3]

    return l*b*h/(ppm*ppm*ppm)

# with open("data.json", "r") as f:
#     data = json.load(f)
# print(len(data['time_windows']))
# print(len(data['demands']))
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

# cvrptw_with_dropped_locations()