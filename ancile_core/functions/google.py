from ancile_core.decorators import transform_decorator, external_request_decorator
from ancile_core.functions.general import get_token
from ancile_web.errors import AncileException

name = 'google'


def _get_primary_metadata(token):
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

@external_request_decorator
def get_primary_calendar_metadata(user=None, **kwargs):

    data = {'output': []}
    token = get_token(user)

    data['calendar'] = _get_primary_metadata(token)
    return data

@external_request_decorator
def get_calendar_events_in_relative_window(user=None, min_time=0,
                                           max_time=1, **kwargs):
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
    events = data.get('events')
    result = event_title in [event['summary'] for event in events]
    data['event_occurring'] = result
    return True

@transform_decorator
def no_events_occurring(data):
    events = data.get('events')
    data['no_events_occurring'] = len(events) == 0
    return True