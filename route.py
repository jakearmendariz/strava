from location import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import mpld3
from scipy.interpolate import interp1d


class Route(object):
    def __init__(self, locations, include_rest = True):
        self.locations = locations
        self.mileage, self.elevation_gain, self.elevation_lost = Location.total_distance_and_elevation(locations)
        self.mileage *= 0.000621371
        self.elevation_gain
        self.elevation_lost
        self.rest_time = 0
        self.total_time = locations[len(locations)-1].time - locations[0].time
        if (include_rest is not True):
            self.total_time = self.active_time()
        
    def distance(self):
        return round(self.mileage, 2)
        
    # Returns a string of how long the run was
    def time(self):
        hours = int(self.total_time/3600)
        minutes = int((self.total_time%3600)/60)
        seconds = int(self.total_time%60)
        if(hours > 0):
            return str(hours) + ":" + str(minutes) + ":" + str(seconds)
        return str(minutes) + ":" + str(seconds)
    
    #Miles per hour, helpful for biking
    def mph(self):
        return self.mileage/(self.total_time/3600)
    
    #Minutes per mile, helpful for running
    def mile_pace(self):
        pace = self.total_time/self.mileage
        minute = int(pace/60)
        second = int(pace%60)
        return str(minute) + ":" + str(second)
    
    def active_time(self):
        self.rest_time = 0
        current_loc = self.locations[0]
        for next_loc in self.locations[1:]:
            if(next_loc.time - current_loc.time > 3):
                self.rest_time += next_loc.time - current_loc.time
            current_loc = next_loc
            
        return self.total_time - self.rest_time
    
    
    def print_summary(self):
        print("milage:", self.distance(), "pace:", self.mile_pace(), "time:", self.time(), "elevation gain:", round(self.elevation_gain, 2), "elevation loss:", round(self.elevation_lost, 2))
        
    # averages the run by an interval of seconds. Then will graph the pace distribution along this
    def graph_by_time(self, seconds):
        pace = np.zeros(int((self.total_time + self.rest_time)/seconds))
        index = 0
        unit_distance = 0
        prev_loc = self.locations[0]
        time_interval = 0
        figure(figsize=(8,6))
        for loc in self.locations[1:]:
            unit_distance += prev_loc.distance_to(loc)
            time_interval += loc.time - prev_loc.time
            # If more than X seconds pass, then calculate the average for that time frame and save into array to be plotted
            if(time_interval > seconds):
                pace[index] = (seconds/60)/(unit_distance* 0.000621371)
                #print(round(pace[index], 2))
                unit_distance = 0
                time_interval = 0
                index += 1
            prev_loc = loc
        pace = pace[:index]
        x = np.arange(index)*seconds /60
        line = pd.Series(data=pace, index=x)
        plt.ylim(ymin=min(pace) - 2)
        plt.ylim(ymax=max(pace) + 2)
        line.plot(linewidth=2.0)
        plt.ylabel('pace')
        plt.xlabel('time')
        plt.show()
        

    def graph_by_distance(self, distance):
        pace = np.zeros(int((self.mileage)/distance))
        altitude = np.zeros(len(pace))
        
        index, unit_distance, time_interval = 0, 0, 0
        prev_loc = self.locations[0]
        figure(figsize=(8,6))
        
        for loc in self.locations[1:]:
            unit_distance += prev_loc.distance_to(loc)*0.000621371
            time_interval += loc.time - prev_loc.time
            # If more than X seconds pass, then calculate the average for that time frame and save into array to be plotted
            if(unit_distance > distance):
                #print("time_interval:", (time_interval/60))
                pace[index] = (time_interval/60)/(distance)
                altitude[index] = prev_loc.alt
                #print(round(pace[index], 2))
                unit_distance, time_interval = 0, 0
                index += 1
                
            prev_loc = loc
        pace = pace[:index]
        pace = normalize_data(pace)
        altitude = altitude[:index]
        if(min(altitude) < 0):
            altitude -= min(altitude)
        altitude /= max(altitude)
        altitude *= max(pace)
        x = np.arange(index)*distance
        smooth_line(x, pace)
        
        #line = pd.Series(data=pace, index=x)
        line1 = pd.Series(data = altitude, index=x)
        plt.ylim(ymin=min(pace) - 2)
        plt.ylim(ymin=0)
        plt.ylim(ymax=max(pace) + 2)
        #line.plot(label="pace", legend=True, linewidth=2.0)
        line1.plot(label="elevation", legend=True, linewidth=2.0)
        plt.ylabel('pace')
        plt.xlabel('time')
        plt.show()
            
def normalize_data(data):
    for i in range(1, len(data)-1):
        if data[i-1] < data[i] and data[i] > data[i+1]:
            if data[i-1]*2 < data[i] and data[i] > data[i+1]*2:
                data[i] = (data[i-1] + data[i+1])/2
            else:
                data[i] = data[i] *.5 + data[i-1]*.25 + data[i+1]*.25
    return data
    
    

def smooth_line(x, y):
    x_new = np.linspace(x.min(), x.max(),500)
    f = interp1d(x, y, kind='quadratic')
    y_smooth=f(x_new)
    plt.plot (x_new,y_smooth, label="pace")
    plt.scatter (x, y, s=10)