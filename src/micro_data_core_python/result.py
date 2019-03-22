from src.micro_data_core_python.decorators import use_type_decorator


class Result:

    def __init__(self):
        self._dp_pair_data = list()

    @use_type_decorator
    def append_dp_data_to_result(self, data):
        print(f'append_dp_data_to_result: {data}')
        self._dp_pair_data.append(data)
        return True
