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

@transform_decorator
def in_geofence(geofence, radius, data=None):
    """
    Simple circular geofence function.
    EXPECTS: 
        'latitude', 'longitude' keys in data
        geofence = (lat, long) pair
        radius - radius of circular fence in meters
    """
    location_tuple = (data.pop('latitude'), data.pop('longitude'))
    result_bool = _in_geofence(geofence, location_tuple, radius)
    data['in_geofence'] = result_bool
    return True  ## REVISIT THIS PRACTICE

@transform_decorator
def in_geofences(geofences, data=None):
    """
    Given a list of circular geofences with labels
    returns the fence (if any) that the location is in.
    
    EXPECTS:
        'latitude' 'longitude' keys in data

    geofences is a list of dictionaries that each have
        'latitude', 'longitude', 'radius', 'label'
    """
    location_tuple = (data.pop('latitude'), data.pop('longitude'))
    filter_lambda = lambda fence: _in_geofence(
                     (fence['latitude'], fence['longitude']),
                     location_tuple,
                     fence['radius'])
    filtered = list(filter(filter_lambda, geofences))
    label = list(map(lambda res: res['label'], filtered))

    result = ''
    if len(label) == 0:
        result = "Location Unknown"
    elif len(label) == 1:
        result = label[0]
    else:
        result = "Error: Overlapping Geofences"

    data['in_geofences'] = result
    return True ## REVISIT THIS PRACTICE