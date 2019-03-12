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
