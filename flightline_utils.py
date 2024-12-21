# flightline_utils.py
import sys
import os
import math
import numpy
from bas_air_unit_network_dataset.exporters.fpl import (
    Fpl,
    Waypoint as FplWaypoint,
    Route as FplRoute,
    RoutePoint as FplRoutePoint,
)
#This is here to make sure the schema files get included in the pyinstaller build
import bas_air_unit_network_dataset.schemas.garmin

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# get the bearing from a pair of coordinates
def get_bearing(lat1, long1, lat2, long2):
    #code below taken from stack overflow https://stackoverflow.com/questions/54873868/python-calculate-bearing-between-two-lat-long
    dLon = (long2 - long1)
    x = math.cos(math.radians(lat2)) * math.sin(math.radians(dLon))
    y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(dLon))
    brng = numpy.arctan2(x,y)
    brng = numpy.degrees(brng)
    return brng
#flip the rows as needed and return an object with the flipped rows
def flip_rows(flightlines,choice, flip):
    if choice == 1:
        start = 0
    elif choice == 2:
        start = 1
    elif choice == 3:
        start = (len(flightlines) % 2) + 1
    elif choice == 4:
        start = len(flightlines) % 2
    if flip == True:
        for i, row in enumerate(flightlines):#This flips every other line, depending on whether we start with the first line or the second
            if (i + start) % 2 == 1:
                flightlines[i] = row[::-1]
    if flip == False and choice == 2:
        for i, row in enumerate(flightlines):
            flightlines[i] = row[::-1] # if you choose 2, flip all the lines
    if choice == 3 or choice == 4: #if you choose two points at the bottom, flip the whole matrix
        flightlines = numpy.flipud(flightlines)
        #todo:  If you implement choice 3/4, add something like this (I think it should work, but not tested):
        #if flip == False and choice == 4:
        #    for i, row in enumerate(flightlines):
        #        flightlines[i] = row[::-1] # if you choose 2, flip all the lines
    return flightlines

#Given a point, bearing and distance, return the new point.  Code from Vasily
def getEndpoint(lat1,lon1,bearing,d):
    R = 6371                     #Radius of the Earth
    brng = math.radians(bearing) #convert degrees to radians
    d = d*1.852                  #convert nautical miles to km
    lat1 = math.radians(lat1)    #Current lat point converted to radians
    lon1 = math.radians(lon1)    #Current long point converted to radians
    lat2 = math.asin( math.sin(lat1)*math.cos(d/R) + math.cos(lat1)*math.sin(d/R)*math.cos(brng))
    lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat1),math.cos(d/R)-math.sin(lat1)*math.sin(lat2))
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return lat2,lon2


#Given a point, bearing and distance, return the new point.  Code from Vasily
def getEndpoint(lat1,lon1,bearing,d):
    R = 6371                     #Radius of the Earth
    brng = math.radians(bearing) #convert degrees to radians
    d = d*1.852                  #convert nautical miles to km
    lat1 = math.radians(lat1)    #Current lat point converted to radians
    lon1 = math.radians(lon1)    #Current long point converted to radians
    lat2 = math.asin( math.sin(lat1)*math.cos(d/R) + math.cos(lat1)*math.sin(d/R)*math.cos(brng))
    lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat1),math.cos(d/R)-math.sin(lat1)*math.sin(lat2))
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return lat2,lon2

def add_endpoints(flightlines, distance=0.5):
    """
    Add endpoints to each flightline.
    
    Args:
    flightlines (list): A list of flightlines, where each flightline is a list of coordinates.
    
    Returns:
    list: A new list of flightlines with endpoints added.
    """
    flightlinesnew = []
    for line in flightlines: #from point 1, get the bearing from point 0 to point 1 and add .5NM.  From point 0, get the bearing from point 1 to point 0 and add .5NM
        point1 = getEndpoint(line[1][0],line[1][1],get_bearing(line[0][0],line[0][1],line[1][0],line[1][1]),distance)
        point2 = getEndpoint(line[0][0],line[0][1],get_bearing(line[1][0],line[1][1],line[0][0],line[0][1]),distance)
        line =  [point2,line[0],line[1],point1]
        flightlinesnew.append(line)
    return flightlinesnew

def flip_rows(flightlines, choice, flip):
    """
    Flip rows of flightlines based on the given choice and flip parameter.
    
    Args:
    flightlines (list): A list of flightlines.
    choice (int): The starting corner choice (1 or 2).
    flip (bool): Whether to use sawtooth pattern (True) or unidirectional (False).
    
    Returns:
    list: A new list of flightlines with rows flipped according to the parameters.
    """
    if choice == 1:
        start = 0
    elif choice == 2:
        start = 1
    elif choice == 3:
        start = (len(flightlines) % 2) + 1
    elif choice == 4:
        start = len(flightlines) % 2
    if flip == True:
        for i, row in enumerate(flightlines):#This flips every other line, depending on whether we start with the first line or the second
            if (i + start) % 2 == 1:
                flightlines[i] = row[::-1]
    if choice == 3 or choice == 4: #if you choose two points at the bottom, flip the whole matrix
        flightlines = numpy.flipud(flightlines)
    return flightlines

def add_keyholes(flightlines):
    """
    Add keyhole points to flightlines.
    
    Args:
    flightlines (list): A list of flightlines.
    
    Returns:
    list: A new list of flightlines with keyhole points added.
    """
    # Implement your keyhole adding logic here
    # This is a placeholder implementation
    flightlinesnew = []
    for i,line in enumerate(flightlines):
        #This was the logic Vasily came up with for turning right vs turning left.  
        # We compare the bearing of the line to the bearing of the first point on the next line
        if  i < len(flightlines)-1: #since we are looking ahead and we don't need keyholes on the final line
            if abs(get_bearing(line[0][0],line[0][1],line[1][0],line[1][1])-get_bearing(line[-1][0],line[-1][1],flightlines[i+1][0][0],flightlines[i+1][0][1])) > 180:
                bearing=get_bearing(line[0][0],line[0][1],line[1][0],line[1][1])-get_bearing(line[-1][0],line[-1][1],flightlines[i+1][0][0],flightlines[i+1][0][1]) +360
            else:
                bearing=get_bearing(line[0][0],line[0][1],line[1][0],line[1][1])-get_bearing(line[-1][0],line[-1][1],flightlines[i+1][0][0],flightlines[i+1][0][1])
            if bearing > 0: #Go out 2NM at +/- 45 degrees depending on bearing
                point1 = getEndpoint(line[-1][0],line[-1][1],get_bearing(line[0][0],line[0][1],line[1][0],line[1][1])+45,2)
            else:
                point1 = getEndpoint(line[-1][0],line[-1][1],get_bearing(line[0][0],line[0][1],line[1][0],line[1][1])-45,2)
            line.append(point1)
        if i>0: #if not the first line, add a keyhole point 3NM out at the beginning of the line
            point1 = getEndpoint(line[0][0],line[0][1],get_bearing(line[1][0],line[1][1],line[0][0],line[0][1]),3)
            line.insert(0,point1)

                
        flightlinesnew.append(line)
    return flightlinesnew


def output_points(output, flightlines):
    """
    Output the flightlines to the given output.
    
    Args:
    output: Either a file path (str) or a file-like object.
    flightlines (list): A list of flightlines to output.
    """
    # Implement your output logic here
    # This function should be able to handle both file paths and file-like objects
    if isinstance(output, str):
        with open(output, 'w') as f:
            for flightline in flightlines:
                for coord in flightline:
                    f.write(str(coord[0]) + "/" + str(coord[1]) + " ")
    else:
        for flightline in flightlines:
            for coord in flightline:
                output.write(str(coord[0]) + "/" + str(coord[1]) + " ")

def fpl_export(flightlines, output_file, prefix):
    """
    Export flightlines to an FPL file.
    
    Args:
    flightlines (list): A list of flightlines to export.
    output_file (str): The path to the output file.
    prefix (str): A three-character prefix for the FPL file.
    """

    path = output_file

    #Build the Waypoints for the FPL file
    waypoints = []
    for lineno, line in enumerate(flightlines):
        for coordno, coord in enumerate(line):
            waypoint = FplWaypoint()
            waypoint.latitude = coord[0]
            waypoint.longitude = coord[1]
            waypoint.comment = ""
            waypoint.type = "USER WAYPOINT"
            waypoint.identifier = prefix + "L" +str(lineno) + "P" + str(coordno)
            waypoints.append(waypoint)

    fpl = Fpl() #from the bas library
    route = FplRoute()
    route_name_string = os.path.basename(output_file).rstrip(".fpl")[:14] # grab the file name, remove the extension, and only use the first 14 characters
    route.name = route_name_string # because we will update route.name if there are more than 94 points, and we want to keep the string around
    print("route name", route.name)
    route.index = 1

    #Build the RoutePoints for the route part of the FPL file
    for route_waypoint in waypoints:
        route_point = FplRoutePoint()
        route_point.waypoint_identifier = route_waypoint.identifier
        route_point.waypoint_type = "USER WAYPOINT"
        #route_point.waypoint_country_code = "__"
        route.points.append(route_point)
        # once you get above 94 points, add a "2" to the filename and the route name, dump it, reset the route, reset the name, and go back to accumulating.  
        # this may be writing multiple times (I don't care) and this keeps all the waypoints in the file
        # it also breaks if you have more than 200 points, but that is unlikely.
        if len(route.points) > 94: 
            path2=path.replace(".fpl", "2.fpl")
            print ("\n FPL path has more than 100 points.  Multiple files being exported to:", path2)
            fpl.waypoints = waypoints
            fpl.route = route
            route.name = route_name_string + "2"
            fpl.dump_xml(path2)
            route = FplRoute()
            route.name = route_name_string
            route.index = 1





    if len(route.points) < 100:
        #Save the FPL file to the path
        print("\nFPL file saved to:", path)
        #path=path.joinpath(file_name_with_date("00_WAYPOINTS_{{date}}.fpl"))
        fpl.waypoints = waypoints
        fpl.route = route
        fpl.dump_xml(path)
    else:
        print ("\n\n*******************There are too many lines in your original KML file")   