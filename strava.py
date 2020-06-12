
def collect_data(filename):
    file = open(filename)
    lines = file.readlines()
    data = open("data", "w+")
    for line in lines:
        if (line.find("<time>") != -1):
            time_index = line.find("T") + 1
            hour = int(line[time_index:time_index+2])
            minute = int(line[time_index+3:time_index+5])
            second = int(line[time_index+6:time_index+8])
            #data.write(str(hour) +" "+ str(minute)+" "+str(second)+ "\n")
            time = hour*3600 + minute*60 + second
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
             
             
            
collect_data("longest_run.txt")
            
            