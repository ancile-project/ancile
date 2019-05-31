from src.micro_data_core_python.decorators import use_type_decorator


class Result:

    def __init__(self):
        self._dp_pair_data = list()

    @use_type_decorator
    def append_dp_data_to_result(self, data, encryption_keys, decrypt_field_list=None):
        # print(f'append_dp_data_to_result: {data}')
        self._dp_pair_data.append(data)
        if decrypt_field_list and isinstance(decrypt_field_list, list):
            dropped = set(encryption_keys.keys()) - set(decrypt_field_list)
            for key in dropped:
                del encryption_keys[key]
        else:
            encryption_keys.clear()
        return True

    def append_keys_to_result(self, data):
        # print(f"Releasing keys: {data._data.keys()}")
        self._dp_pair_data.append({'data_keys': list(data._data.keys())})

        return True