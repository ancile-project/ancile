from src.micro_data_core_python.policy_processor import PolicyProcessor


@PolicyProcessor.decorator
def asdf():
    print('FUNC: asdf')


@PolicyProcessor.decorator
def qwer():
    print('FUNC: qwer')


@PolicyProcessor.decorator
def zxcv():
    print('FUNC: zxcv')


@PolicyProcessor.decorator
def get_location():
    print("FUNC: get_location")
    return True


@PolicyProcessor.decorator
def filter_floor(floor):
    print("FUNC: filter_floor" + str(floor))
    return True