from src.micro_data_core_python.decorators import comparison_decorator
import src.micro_data_core_python.time as ancile_time

@comparison_decorator
def in_time_window(data, lower_str, upper_str, weekday_list=None):
    if (weekday_list is not None and
       not ancile_time.today_in_list(weekday_list)):
        return False
    else:
        return ancile_time.today_in_time_window(lower_str, upper_str)