from src.micro_data_core_python.decorators import transform_decorator, external_request_decorator
from src.micro_data_core_python.errors import AncileException

@external_request_decorator
def get_primary_calendar_metadata(data, token=None, **kwargs):
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

    data['calendar'] = primary[0]
    return True

@external_request_decorator
def get_calendar_events_in_relative_window(data, token=None, 
                    min_time=0, max_time=1, **kwargs):
    from datetime import datetime, timedelta, timezone
    import requests

    def format_time(unformatted):
        return unformatted.isoformat()
        # return unformatted.strftime("%Y-%m-%dT%H:%M:%S%z")

    now = datetime.now(timezone.utc).astimezone()
    lower = format_time(now - timedelta(minutes=min_time))
    upper = format_time(now + timedelta(minutes=max_time))

    calendar = data.pop('calendar')

    target_url = "https://www.googleapis.com/calendar/v3/calendars/" + \
                calendar["id"] + "/events?singleEvents=true&timeMin=" + \
                lower + "&timeMax=" + upper

    r = requests.get(target_url, 
            headers={'Authorization': "Bearer " + token})
    
    if r.status_code != 200:
        raise AncileException("Request Error")

    data['events'] = r.json()['items']
    return True

@transform_decorator
def event_occuring(data, event_title=None):
    events = data.pop('events')
    result = event_title in [event['summary'] for event in events]
    data['event_occuring'] = result
    return True

@transform_decorator
def no_events_occuring(data):
    events = data.pop('events')
    data['no_events_occuring'] = len(events) == 0
    return True