from src.micro_data_core_python.decorators import return_data_decorator

@return_data_decorator
def return_data(data):
    print(f'FUNC: return. data: {data}')
    return data
