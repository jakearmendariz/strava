from route import *

def collect_data(filename):
    file = open(filename)
    lines = file.readlines()
    data = open("data", "w+")
    firstline = True
    start_time = 0
    for line in lines:
        if (line.find("<time>") != -1):
            time_index = line.find("T") + 1
            hour = int(line[time_index:time_index+2])
            minute = int(line[time_index+3:time_index+5])
            second = int(line[time_index+6:time_index+8])
            time = hour*3600 + minute*60 + second
            if firstline:
                start_time = time
                firstline = False
            time -= start_time
            data.write(str(time) + " ")
        
        if (line.find("<trkpt") != -1):
            lat_index = line.find("lat") + 5
            lat = float(line[lat_index:lat_index+line[lat_index:].find("\"")])
            lon_index = line.find("lon") + 5
            lon = float(line[lon_index:lon_index+line[lon_index:].find("\"")])
            data.write(str(lat) + " " + str(lon) + " ")
            
        if (line.find("<ele>") != -1):
            elev_index = line.find(">") + 1
            elev = float(line[elev_index: elev_index+line[elev_index:].find("<")])
            data.write(str(elev) + "\n")
            
def build_run(locations):
    file = open("data")
    lines = file.readlines()
    for line in lines:
        line = line.split()
        if (len(line) > 1):
         locations.append(Location(float(line[0]), float(line[1]), float(line[2]), float(line[3])))
             
             
locations = []    
collect_data("Afternoon_run.gpx")
build_run(locations)
route = Route(locations, include_rest = True)
route.print_summary()
#route.graph_by_time(60)
route.graph_by_distance(.1)


            
            