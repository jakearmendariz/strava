from math import sin, cos, sqrt, pi

class Location(object):
    """Data structure for holding location information"""

    EARTH_RADIUS = 6378100 # in meters

    def __init__(self, time, lat, lon, altitude=0.0):
        """
        Create a new instance with the given
        latitude, longitude, altitude, and timestamp
        """
        self.lat = lat
        self.lon = lon
        self.alt = altitude
        self.time = time
        self.distance_covered = 0


    def _as_cartesian(self):
        """Returns a representation of the location in (x, y, z)"""
        lat_radians = self.lat * pi / 180
        lon_radians = self.lon * pi / 180
        radius = Location.EARTH_RADIUS + self.alt

        x = radius * cos(lat_radians) * sin(lon_radians)
        y = radius * sin(lat_radians)
        z = radius * cos(lat_radians) * cos(lon_radians)
        return (x, y, z)


    def distance_to(self, other_location):
        """Returns the distance in meters to `other_location`"""

        x1, y1, z1 = self._as_cartesian()
        x2, y2, z2 = other_location._as_cartesian()
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


    @staticmethod
    def total_distance(locations):
        """Computes the total distance along a path, in meters"""

        if len(locations) < 2:
            return 0.0

        total = 0.0
        current_loc = locations[0]

        for next_loc in locations[1:]:
            total += current_loc.distance_to(next_loc)
            next_loc.distance_covered = total
            current_loc = next_loc

        return total
    
    @staticmethod
    def total_distance_and_elevation(locations):
        """Computes the total distance along a path, in meters"""

        if len(locations) < 2:
            return 0.0

        total = 0.0
        elevation_gain = 0
        elevation_lost = 0
        current_loc = locations[0]

        for next_loc in locations[1:]:
            total += current_loc.distance_to(next_loc)
            next_loc.distance_covered = total
            if(current_loc.alt > next_loc.alt):
                elevation_lost += current_loc.alt - next_loc.alt
            else:
                elevation_gain += next_loc.alt - current_loc.alt
            current_loc = next_loc
        

        return (total, elevation_gain, elevation_lost)