import simplekml
import csv
import numpy as np
import random

kml = simplekml.Kml()
routes = []
points = []
with open("./driver_paths.csv", 'r') as file:
  file = csv.reader(file)
  for row in file:
    try:
        route_number = int(row[0].split()[1])
        while len(routes)<route_number:
            routes.append([])
        latitude = float(row[1])
        longitude = float(row[2])
        awb = row[4]
        coord = (longitude, latitude)
        routes[route_number-1].append(coord)
        pnt = kml.newpoint(name=awb, coords=[coord])
        pnt.description = awb
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'


    except:
        continue

for i in range (len(routes)):
    route = routes[i]
    ls = kml.newlinestring(name='Route - '+str(i+1), description="Route - "+str(i+1))
    ls.coords = np.array(route)
    ls.altitudemode = simplekml.AltitudeMode.relativetoground
    ls.extrude = 1
    ls.style.linestyle.color = simplekml.Color.rgb(random.randint(0,255), random.randint(0,255), random.randint(0,255))
    ls.style.linestyle.width= 3  # 10 pixels

kml.save("Points_and_Line.kml")
