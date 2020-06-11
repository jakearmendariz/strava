"""
Helper to convert GPX files to CSV files for analysis.

Created by Trevor Phillips
"""

import os
import json

try:
    import urllib.request
except:
    print('You need to use Python3')
    exit()

import xml.etree.ElementTree as ET
from datetime import datetime
from math import sin, cos, sqrt, pi


_API_KEY = os.environ['GOOGLE_ELEVATION_API_KEY']
_BASE_URL = 'https://maps.googleapis.com/maps/api/elevation/json'


class Location(object):
    """Data structure for holding location information"""

    EARTH_RADIUS = 6378100 # in meters

    def __init__(self, lat, lon, altitude=0.0, time=None):
        """
        Create a new instance with the given
        latitude, longitude, altitude, and timestamp
        """

        self.lat = lat
        self.lon = lon
        self.alt = altitude
        self.time = time


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
            current_loc = next_loc

        return total


    def csv_str(self):
        """String representation for CSV file"""

        fmt = "%Y-%m-%d'T'%H:%M:%S'Z'"
        time_str = self.time.strftime(fmt) if self.time is not None else ''

        return '{},{},{},0,0,-1,-1,{}'.format(
            self.lat, self.lon, self.alt, time_str
        )


def is_gpx(filepath):
    """Returns true if the filepath is a GPX file otherwise False"""

    ext_index = filepath.rfind('.')

    if ext_index == -1 or \
    filepath[ext_index + 1:].lower() != 'gpx' or \
    os.path.isfile(filepath) is False:
        return False

    return True


def _parse_altitudes(json_object):
    """Parse array of altitudes from Google Elevation API JSON"""

    results = json_object['results']
    return [item['elevation'] for item in results]


def _write_locations_to_csv(locations, csv_filepath):
    """Write array of Location objects as CSV to the given filepath"""

    header = 'latitude,longitude,altitude,horizonal_acc,' + \
        'vertical_acc,course,speed,timestamp'
    location_strings = [loc.csv_str() for loc in locations]
    csv_content = '\n'.join([header] + location_strings)

    with open(csv_filepath, 'w+') as csv_file:
        csv_file.write(csv_content)


def _is_onthegomap_gpx(filepath):
    """
    Returns True if `filepath` is a GPX file from
    https://onthegomap.com and False otherwise.
    """

    if is_gpx(filepath) is False:
        return False

    return 'https://onthegomap.com' in open(filepath).read()


def _onthegomap_gpx_to_csv(gpx_filepath, csv_filepath):
    """
    Convert a GPX file at location `gpx_filepath` which was generated
    using the online tool at https://onthegomap.com into a CSV file
    with altitude, latitude, and longitude information, stored at the
    given `csv_filepath` (existing file will be overwritten).
    """

    root = ET.parse(gpx_filepath).getroot()
    prefix = root.tag.replace('gpx', '')
    path = './{}rte/{}rtept'.format(prefix, prefix)

    locations, location_strings = [], []

    for point in root.findall(path):
        lat, lon = point.get('lat'), point.get('lon')
        locations.append(Location(lat, lon))
        location_strings.append('{},{}'.format(lat ,lon))

    location_str = '|'.join(location_strings)
    altitude_api_query = '{}?locations={}&key={}'.format(
        _BASE_URL, location_str, _API_KEY
    )

    url = urllib.request.urlopen(altitude_api_query)
    data = url.read()
    encoding = url.info().get_content_charset('utf-8')
    json_response = json.loads(data.decode(encoding))

    altitudes = _parse_altitudes(json_response)
    assert len(altitudes) == len(locations)

    for i, loc in enumerate(locations):
        loc.alt = altitudes[i]

    _write_locations_to_csv(locations, csv_filepath)


def _is_garmin_gpx(filepath):
    """
    Returns True if `filepath` is a GPX file from
    Garmin and False otherwise.
    """

    if is_gpx(filepath) is False:
        return False

    return 'garmin.com' in open(filepath).read()


def _garmin_gpx_to_csv(gpx_filepath, csv_filepath):
    """
    Convert a GPX file at location `gpx_filepath` which was generated
    from a Garmin device into a CSV file with altitude, latitude,
    longitude, and timestamp information, stored at the
    given `csv_filepath` (existing file will be overwritten).
    """

    root = ET.parse(gpx_filepath).getroot()
    prefix = root.tag.replace('gpx', '')
    path = './{}trk/{}trkseg/{}trkpt'.format(prefix, prefix, prefix)

    locations = []

    for point in root.findall(path):
        lat, lon = point.get('lat'), point.get('lon')
        alt = point.find('{}ele'.format(prefix)).text
        time_str = point.find('{}time'.format(prefix)).text
        fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
        time = datetime.strptime(time_str, fmt)
        locations.append(Location(lat, lon, altitude=alt, time=time))

    _write_locations_to_csv(locations, csv_filepath)


def gpx_to_csv(gpx_filepath):
    """
    Convert a GPX file at location `gpx_filepath` into a CSV file,
    with the same filename before the .gpx extension and in the same
    directory as the GPX file (any existing file will be overwritten).
    """

    csv_path = gpx_filepath.replace('GPX', 'gpx').replace('.gpx', '.csv')

    if _is_garmin_gpx(gpx_filepath):
        _garmin_gpx_to_csv(gpx_filepath, csv_path)
    elif _is_onthegomap_gpx(gpx_filepath):
        _onthegomap_gpx_to_csv(gpx_filepath, csv_path)
    else:
        print('This GPX format is not supported')

    return csv_path

gpx_to_csv("Lunch_Run.gpx")