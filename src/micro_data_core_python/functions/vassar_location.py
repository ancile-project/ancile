from src.micro_data_core_python.decorators import transform_decorator
from src.micro_data_core_python.functions import location

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
    result_bool = location._in_geofence(geofence, location_tuple, radius)
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
    filter_lambda = lambda fence: location._in_geofence(
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