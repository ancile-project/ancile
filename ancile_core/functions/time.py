from ancile_core.decorators import comparison_decorator
import ancile_core.time as ancile_web_time

@comparison_decorator
def in_time_window(data, lower_str, upper_str, weekday_list=None):
    if (weekday_list is not None and
       not ancile_web_time.today_in_list(weekday_list)):
        return False
    else:
        return ancile_web_time.today_in_time_window(lower_str, upper_str)