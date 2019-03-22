from src.micro_data_core_python.decorators import transform_decorator

def _haversine(pt1, pt2):
    """
    pt1/pt2 = (lat,long)
    The great circle distance between two points
    specified in decimal degrees, given in meters
    """
    RADIUS = 63721008.8 # Earth radius in meters
    from math import radians, cos, sin, asin, sqrt
    lat1, long1 = pt1
    lat2, long2 = pt2

    diff_lat = radians(lat2) - radians(lat1)
    diff_long = radians(long2) - radians(long1)

    a = sin(diff_lat/2)**2 + cos(lat1) * cos(lat2) * sin(diff_long/2)**2
    c = 2 * asin(sqrt(a))

    return RADIUS * c

def _in_geofence(pt1, pt2, radius):
    return _haversine(pt1, pt2) <= radius

