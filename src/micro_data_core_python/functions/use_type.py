from src.micro_data_core_python.decorators import use_type_decorator


@use_type_decorator
def return_data_to_the_program(data):
    print(f'FUNC: return. data: {data}')
    return data
