"""
This module contains functions for transforming and operating on location data
in a way that is agnostic to data source. These functions are primarily wrapped
over by Ancile functions that are configured for a particular data source's
format.
"""
from ancile_core.decorators import transform_decorator
from geopy.distance import distance
from geopy import Point
from numpy import random


def _in_geofence(pt1, pt2, radius):
    """
    Determine if the distance between pt1 and pt2 is less than or equal to
    the given radius.

    :param pt1: A point (lat, long)
    :param pt2: A point (lat, long)
    :param radius: A number
    :return: True if the distance between the two points is less than or equal
             to the given radius, False otherwise.
    """
    return distance(pt1, pt2).m <= radius

def _fuzz_location(lat, lon, radius):
    """
    Shift the given point randomly to some location within the specified
    radius.

    :param lat: The latitude of the point.
    :param lon: The longitude of the point.
    :param radius: The radius describing the maximal possible shift distance
                   from the given point in meters.
    :return: A shifted point that is at most radius meters from the starting
             point. Returned as (latitude, longitude)
    """
    start = Point(lat, lon)
    length = random.uniform(0, radius)
    bearing = random.uniform(0, 360)

    distance_vec = distance(meters=length)

    new_pt = distance_vec.destination(start, bearing)
    return new_pt.latitude, new_pt.longitude