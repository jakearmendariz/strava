import math
class Stats():
    def __init__(self, write_to, start):
        self.start_time = int(start[0])
        self.total_distance = 0
        self.total_elevation_gain = 0
        self.total_elevation_loss = 0
        self.file = write_to
        
        self.latitude = float(start[1])
        self.longitude = float(start[2])
    
    def update(self, data):
        time_elapsed = int(data[0]) - self.start_time
        if(len(data) > 1):
            self.total_distance += self.distance_moved(float(data[1]), float(data[2]))*3767.4 / 63.39
            self.latitude, self.longitude = float(data[1]), float(data[2])
            self.file.write(str(time_elapsed) + " " + str(self.total_distance) + "\n")
        
        
    def distance_moved(self, latitude, longitude):
        return math.sqrt((latitude - self.latitude)**2 + (longitude - self.longitude)**2)

def transform_data(filename):
    file = open(filename)
    lines = file.readlines()
    data = open("run", "w+")
    stats = Stats(data, lines[0].split())

    for i in range(1, len(lines)):
        stats.update(lines[i].split())

transform_data("data")
        