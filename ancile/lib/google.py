"""
This module defines Ancile functions to work with data coming from Google.

Currently supports the following data sources:
- Google Calendar
"""
from core.decorators import transform_decorator, external_request_decorator
from core.functions.general import get_token
from ancile.utils.errors import AncileException

name = 'google'


# ============================================================================
#  Google Calendar Functions
# ============================================================================

def _get_primary_metadata(token):
    """
    Retrieve the metadata for a given user's primary google calendar.

    :param token: A Google access token with calendar scopes.
    :return: Primary calendar metadata as a dictionary.
    """
    import requests
    target_url = "https://www.googleapis.com/calendar/v3/users/me/calendarList"
    r = requests.get(target_url,
                     headers={'Authorization': "Bearer " + token})

    if r.status_code != 200:
        raise AncileException("Request Error")

    calendar_list = r.json()
    primary = [x for x in calendar_list['items'] if x.get("primary")]

    if not primary:
        raise AncileException("No Calendar")

    return primary[0]

@external_request_decorator()
def get_primary_calendar_metadata(user=None, **kwargs):
    """
    Retrieve primary calendar metadata as an Ancile function.

    :param user: A UserSpecific data object.
    :return: Primary calendar metadata dictionary.
    """
    data = {'output': []}
    token = get_token(user)

    data['calendar'] = _get_primary_metadata(token)
    return data

@external_request_decorator()
def get_calendar_events_in_relative_window(user=None, min_time=0,
                                           max_time=1, **kwargs):
    """
    Retrieve Google calendar events for the primary calendar that are occurring
    within min_time minutes before now and max_time minutes after now.

    :param user: A UserSpecific data structure.
    :param min_time: The lower bound of the event window, given in minutes
                     before the current moment.
    :param max_time: The upper bound of the event window, given in minutes
                     after the current moment.
    :return: ['events']. Data for all events occurring in the window
                         (now - min, now + max) listed in the user's primary
                         google calendar.
    """
    from datetime import datetime, timedelta, timezone
    import requests

    data = {'output': []}
    token = get_token(user)

    def format_time(unformatted):
        return unformatted.isoformat()

    cal_id = _get_primary_metadata(token)['id']

    now = datetime.now(timezone.utc).astimezone()
    lower = format_time(now - timedelta(minutes=min_time))
    upper = format_time(now + timedelta(minutes=max_time))

    target_url = "https://www.googleapis.com/calendar/v3/calendars/" + \
                 cal_id + "/events?singleEvents=true&timeMin=" + \
                 lower + "&timeMax=" + upper

    r = requests.get(target_url,
                     headers={'Authorization': "Bearer " + token})

    if r.status_code != 200:
        raise AncileException("Request Error")

    data['events'] = r.json()['items']
    return data

@transform_decorator
def event_occurring(data, event_title=None):
    """
    Check if a specified event title occurs in the list of occurring events.
        Expects: ['events']

    :param data: A DataPolicyPair's data field.
    :param event_title: String with the name of the event
    :return: ['event_occurring']. T/F based on whether or not the event is
             present
    """
    events = data.get('events')
    result = event_title in [event['summary'] for event in events]
    data['event_occurring'] = result

@transform_decorator
def no_events_occurring(data):
    """
    Check if no events are in the list of occurring events.
        Expects: ['events']

    :param data: A DataPolicyPair's data field
    :return: ['no_events_occurring']. T/F based on whether or not events are
             present.
    """
    events = data.get('events')
    data['no_events_occurring'] = len(events) == 0