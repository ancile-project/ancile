from ancile_core.decorators import transform_decorator
from geopy.distance import distance
from geopy import Point
from numpy import random


def _in_geofence(pt1, pt2, radius):
    return distance(pt1, pt2).m <= radius

def _fuzz_location(lat, lon, radius):
    start = Point(lat, lon)
    length = random.uniform(0, radius)
    bearing = random.uniform(0, 360)

    distance_vec = distance(meters=length)

    new_pt = distance_vec.destination(start, bearing)
    return new_pt.latitude, new_pt.longitude