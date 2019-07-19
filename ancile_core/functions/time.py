"""
This module defines Ancile functions to work with temporal information inside
Ancile.
"""
from ancile_core.decorators import comparison_decorator
import ancile_core.time as ancile_web_time

@comparison_decorator
def in_time_window(data, lower_str, upper_str, weekday_list=None):
    """
    Determine if the current time is within a given time window on the given
    either today, if weekday_list is not given, or on any of the listed days,
    if it is.

    :param data: A DataPolicyPair's data field.
    :param str lower_str: A string representing the lower bound on the time
                          window, formatted "hh:mm" in 24-hour time.
    :param str upper_str: A string representing the upper bound on the time
                          window, formatted "hh:mm" in 24-hour time.
    :param list weekday_list: An optional list of days to consider.
    :return: True if the current time is in the specified window, False
             otherwise.

    example:
        in_time_window(data, "09:00", "17:00", ['mon', 'tue', 'wed', 'thur',
                                                'fri'])
        returns true only if the current time is between 9am and 5pm during a
        weekday.
    """
    if (weekday_list is not None and
       not ancile_web_time.today_in_list(weekday_list)):
        return False
    else:
        return ancile_web_time.today_in_time_window(lower_str, upper_str)