import json
from cryptography.fernet import Fernet


def encrypt(data_dict):
    keys_dict = dict()
    encrypted_dict = dict()
    for name, value in data_dict.items():
        if name in ['output']:
            continue
        key = Fernet.generate_key()
        f = Fernet(key)
        string_val = json.dumps(value)
        token = f.encrypt(str.encode(string_val))
        keys_dict[name] = key.decode("utf-8")
        encrypted_dict[name] = token.decode("utf-8")
    return keys_dict, encrypted_dict


def release_keys(keys_dict, data_dict):
    sub_dict = {k: keys_dict[k] for k in data_dict.keys() if k != 'output'}
    return sub_dict