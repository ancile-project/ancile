from src.micro_data_core_python.decorators import transform_decorator, external_request_decorator
from src.micro_data_core_python.functions import location
from src.micro_data_core_python.errors import AncileException
import requests

name = 'vassar_data_service'


@external_request_decorator
def get_last_location(data, token=None):
    r = requests.get('https://campusdataservices.cs.vassar.edu/api/last_known',
                     headers={'Authorization': f'Bearer {token}'})
    if r.status_code == 200:
        data.update(r.json())
    else:
        raise AncileException(f"Request error: {r.json()}")

@transform_decorator
def in_geofence(geofence, radius, data=None):
    """
    Simple circular geofence function.
    EXPECTS: 
        'latitude', 'longitude' keys in data
        geofence = (lat, long) pair
        radius - radius of circular fence in meters
    """
    location_tuple = (data.get('latitude'), data.get('longitude'))
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
    location_tuple = (data.get('latitude'), data.get('longitude'))
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
    return True
