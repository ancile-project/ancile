from ancile_core.decorators import transform_decorator, external_request_decorator
from ancile_web.errors import AncileException

name="azure"

@external_request_decorator
def get_available_rooms(data, floor, token=None):
    import requests

    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}

    url = "https://graph.microsoft.com/beta/me/findMeetingTimes"
    start, end = get_start_end_time()
    js = get_available_by_floor(floor, start, end)
    print(headers)
    result = requests.post(url=url, headers=headers, json=js)
    available_rooms = list()
    if result.status_code != 200:
        data['output'].append(result.text)
        return True

    else:
        msft_resp = result.json()
        for x in msft_resp['meetingTimeSuggestions'][0]["attendeeAvailability"]:
            if x["availability"] == "free":
                available_rooms.append(room_by_email(x["attendee"]['emailAddress']['address']))
    data['rooms'] = available_rooms
    return  True

@external_request_decorator
def book_room(data, room, token=None):
    import requests
    import json

    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}

    url = "https://graph.microsoft.com/beta/me/calendar/events"
    start, end = get_start_end_time()
    room_full = get_room_by_no(room)

    book_json = create_booking_json(user="User",
                                    room=room_full,
                                    time_start=start.isoformat(),
                                    time_end=end.isoformat())
    print(json.dumps(book_json, indent=4))
    print(headers)
    result = requests.post(url=url, headers=headers, json=book_json)
    if result.status_code != 200:
        data['output'].append(result.text)
        return True

    data['booking_result'] = 'success'
    return  True


def get_available_by_floor(floor, time_start, time_end):
    rooms = get_rooms_by_floor(floor)
    available_rooms = list()
    rooms_json = check_floor_json(rooms, time_start.isoformat(), time_end.isoformat())


    return rooms_json


def get_room_by_no(no):

    for room in rooms:
        if ('Bloomberg %03d' % int(no)) in room['name']:
            return room

    return None


def get_rooms_by_floor(floor):
    room_list = list()
    if int(floor) in [0,1,2,3,4]:
        for room in rooms:
            if 'Bloomberg {0}'.format(floor) in room['name']:
                room_list.append(room)

    return room_list


def parse_time_room(iso_datetime):
    date_normal, iso_time = iso_datetime.split('T')
    hour, minute, _ = iso_time.split(':')
    return '{0} {1}:{2}'.format(date_normal, hour, minute)


def get_meeting_info(meeting):
    id = meeting['id']
    start =  parse_time_room(meeting["start"]['dateTime'])
    end = parse_time_room(meeting["end"]['dateTime'])
    location = meeting['location']['displayName']
    timeZone = meeting['end']['timeZone']
    return {'id': id, 'start': start, 'end': end, 'location':location, 'timeZone': timeZone}

def room_by_email(room_email):
    for room in rooms:
        if room["address"] == room_email:
            return ' '.join(room['name'].split()[3:])

    return 'No room found for {0}.'.format(room_email)


def get_start_end_time():
    from datetime import datetime, timedelta
    from pytz import timezone

    eastern = timezone('US/Eastern')
    time_start = datetime.now(eastern)
    if time_start.minute >= 20 and time_start.minute < 50:
        time_start = time_start.replace(microsecond=0, second=0, minute=30, tzinfo=None)
    elif time_start.minute >= 50:
        if time_start.hour < 23:
            time_start = time_start.replace(microsecond=0, second=0, minute=0, hour=time_start.hour + 1, tzinfo=None)
        else:
            time_start = time_start.replace(microsecond=0, second=0, minute=0, hour=0, day=time_start.day + 1,
                                            tzinfo=None)
    else:
        time_start = time_start.replace(microsecond=0, second=0, minute=0, tzinfo=None)

    time_end = time_start + timedelta(hours=1)

    return time_start, time_end

rooms = [
        {
            "name": "Tech - Bloomberg 061 (50 VC)",
            "address": "cutech-bloomberg-061@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 071 (50 VC)",
            "address": "cutech-bloomberg-071@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 081 (50 VC)",
            "address": "cutech-bloomberg-081@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 091 (50 VC)",
            "address": "cutech-bloomberg-091@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 131 (200 VC)",
            "address": "cutech-bloomberg-131@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 161 (50 VC)",
            "address": "cutech-bloomberg-161@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 165 (50 VC)",
            "address": "cutech-bloomberg-165@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 201 (20 VC)",
            "address": "cutech-bloomberg-201@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 205 (42 D)",
            "address": "cutech-bloomberg-205@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 212 (5 D)",
            "address": "cutech-bloomberg-212@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 216 (5 D)",
            "address": "cutech-bloomberg-216@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 238 (8)",
            "address": "cutech-bloomberg-238@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 240 (20)",
            "address": "cutech-bloomberg-240@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 252 (5 D)",
            "address": "cutech-bloomberg-252@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 254 (5 D)",
            "address": "cutech-bloomberg-254@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 256 (5 D)",
            "address": "cutech-bloomberg-256@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 260 (5 D)",
            "address": "cutech-bloomberg-260@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 267 (6 D)",
            "address": "cutech-bloomberg-267@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 268 (5 D)",
            "address": "cutech-bloomberg-268@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 275 (6 D)",
            "address": "cutech-bloomberg-275@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 277 (6)",
            "address": "cutech-bloomberg-277@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 287 (5 D)",
            "address": "cutech-bloomberg-287@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 289 (5 D)",
            "address": "cutech-bloomberg-289@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 291 (5 D)",
            "address": "cutech-bloomberg-291@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 301 (20 VC)",
            "address": "cutech-bloomberg-301@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 309 (21)",
            "address": "cutech-bloomberg-309@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 310 (5 D)",
            "address": "cutech-bloomberg-310@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 318 (5 D)",
            "address": "cutech-bloomberg-318@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 320 (5 D)",
            "address": "cutech-bloomberg-320@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 335 (5)",
            "address": "cutech-bloomberg-335@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 338 (10 VC)",
            "address": "cutech-bloomberg-338@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 340 (44)",
            "address": "cutech-bloomberg-340@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 356 (5 D)",
            "address": "cutech-bloomberg-356@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 360 (5 D)",
            "address": "cutech-bloomberg-360@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 362 (5 D)",
            "address": "cutech-bloomberg-362@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 364 (5 D)",
            "address": "cutech-bloomberg-364@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 366 (5 D)",
            "address": "cutech-bloomberg-366@tech.cornell.edu"
        },

        {
            "name": "Tech - Bloomberg 367 (5 D)",
            "address": "cutech-bloomberg-367@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 368 (5 D)",
            "address": "cutech-bloomberg-368@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 375 (8 D)",
            "address": "cutech-bloomberg-375@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 377 (6 D)",
            "address": "cutech-bloomberg-377@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 381 (5)",
            "address": "cutech-bloomberg-381@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 397 (8 VC)",
            "address": "cutech-bloomberg-397@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 398 (8 VC)",
            "address": "cutech-bloomberg-398@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 401 (20 VC)",
            "address": "cutech-bloomberg-401@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 477 (3)",
            "address": "cutech-bloomberg-477@tech.cornell.edu"
        },
        {
            "name": "Tech - Bloomberg 497 (15 VC)",
            "address": "cutech-bloomberg-497@tech.cornell.edu"
        }
    ]

def check_floor_json(rooms, time_start, time_end):
    mjson = {
        "isOrganizerOptional": "True",
        "attendees":

            [{
                "type": "required",
                "emailAddress": x
            } for x in rooms]
            ,
        "timeConstraint": {
            "activityDomain": "unrestricted",
            "timeslots": [
                {
                    "start": {
                        "dateTime": time_start,
                        "timeZone": "Eastern Standard Time"
                    },
                    "end": {
                        "dateTime": time_end,
                        "timeZone": "Eastern Standard Time"
                    }
                }
            ]
        },
        "meetingDuration": "PT1H",
        "returnSuggestionReasons": "true",
        "minimumAttendeePercentage": "1"
    }

    return mjson


def find_room_json(room, time_start, time_end):
    mjson = {
              "isOrganizerOptional": "True",
              "attendees":
                  [
                    {
                        "type": "required",
                        "emailAddress": room
                    }
                  ],
              "timeConstraint": {
                "activityDomain": "unrestricted",
                "timeslots": [
                  {
                    "start": {
                      "dateTime": time_start,
                      "timeZone": "Eastern Standard Time"
                    },
                    "end": {
                      "dateTime": time_end,
                      "timeZone": "Eastern Standard Time"
                    }
                  }
                ]
              },
              "meetingDuration": "PT1H",
              "returnSuggestionReasons": "true",
              "minimumAttendeePercentage": "100"
            }

    return mjson


def create_booking_json(user, room, time_start, time_end):
    mjson = {
      "subject": 'Meeting for {0}.'.format(user),
      "body": {
        "contentType": "HTML",
        "content": "This event is created by RoomParking Slackbot, contact Eugene (eugene@cs.cornell.edu) for help."
      },
      "start": {
        "dateTime": time_start,
        "timeZone": "Eastern Standard Time"
      },
      "end": {
        "dateTime": time_end,
        "timeZone": "Eastern Standard Time"
      },
      "location": {
        "displayName": room['name']
      },
      "attendees": [
        {
          "emailAddress": room,
          "type": "resource"
        }
      ]
    }

    return mjson
