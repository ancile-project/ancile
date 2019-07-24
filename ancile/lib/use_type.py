from ancile.core.decorators import use_type_decorator


@use_type_decorator
def return_data_to_the_program(data, encryption_keys, decrypt_field_list=None):
    print(f'FUNC: return. data: {data}')
    if decrypt_field_list and isinstance(decrypt_field_list, list):
        dropped = set(encryption_keys.keys()) - set(decrypt_field_list)
        for key in dropped:
            del encryption_keys[key]
    else:
        encryption_keys.clear()
    return data, encryption_keys
