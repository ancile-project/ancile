"""
This module defines Ancile functions to work with data coming from the Vassar
Campus Data server at campusdataservices.cs.vassar.edu.
"""

from ancile.core.decorators import *
from ancile.lib.general import get_token
from ancile.lib import location
from ancile.utils.errors import AncileException
import requests

name = 'cds'


@ExternalDecorator()
def get_last_location(user):
    """
    Make a request to the last location API with the user's access token.

    :param user: A UserSpecific data structure
    :return: The last location information given by the server.
    """
    token = get_token(user)
    data = {'output': []}
    r = requests.get('https://campusdataservices.cs.vassar.edu/api/last_known',
                     headers={'Authorization': f'Bearer {token}'})
    if r.status_code == 200:
        data.update(r.json())
    else:
        raise AncileException(f"Request error: {r.json()}")

    return data


@TransformDecorator()
def in_geofence(geofence, radius, data=None):
    """
    Determine if the user is inside the given circular geofence.
    EXPECTS:
        'latitude', 'longitude' keys

    :param geofence: (lat, long) pair marking the center of the geofence
    :param radius: radius of circular fence in meters
    :return: ['in_geofence'] T if the point is within the fence, F otherwise.
    """
    location_tuple = (data.get('latitude'), data.get('longitude'))
    result_bool = location._in_geofence(geofence, location_tuple, radius)
    data['in_geofence'] = result_bool


@TransformDecorator()
def in_geofences(geofences, data=None):
    """
    Determine if the user is within any of a given list of circular geofences.
    EXPECTS:
        'latitude' 'longitude' keys


    :param list geofences: A list of dictionaries containing the following fields,
                          'latitude', 'longitude', 'radius', 'label'
    :return: ['in_geofences']. The label of the geofence the user is in,
             "Location Unknown" if they are in no fence.
    :raises: AncileException if the user is in multiple fences.
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
        raise AncileException("Specified Geofences must not overlap")

    data['in_geofences'] = result


def in_geofences_bool(geofences, data=None):
    """ A wrapper around in_geofences that reduces the value to a boolean"""
    in_geofences(geofences=geofences, data=data)

    val = data._data.pop('in_geofences')
    data._data['in_geofences'] = val not in ["Location Unknown"]


@TransformDecorator()
def fuzz_location(data, radius):
    """
    Fuzz a location point by moving it to some random location with the specified
    radius.
        Expects: 'latitude', 'longitude'

    :param data: A DataPolicyPair's data field.
    :param radius: The maximal distance the location may be displaced.
    :return: The fuzzed location point ['latitude', 'longitude']
    """
    new_lat, new_long = location._fuzz_location(data['latitude'],
                                                data['longitude'],
                                                radius)
    data['latitude'] = new_lat
    data['longitude'] = new_long
