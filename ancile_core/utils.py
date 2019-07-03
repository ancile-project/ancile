import json
from cryptography.fernet import Fernet
import logging
logger = logging.getLogger(__name__)


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

def _decrypt(key, data):
    if isinstance(key, str):
        f = Fernet(key)
    elif isinstance(key, dict) and isinstance(data, dict):
        out = dict()
        for name in key:
            k = Fernet(key[name])
            out[name] = json.loads(k.decrypt(bytes(data[name], 'utf8')))
        return out
    else:
        raise ValueError()

    if isinstance(data, dict):
        for name in data:
            data[name] = json.loads(f.decrypt(bytes(data[name], 'utf8')))
        return data
    elif isinstance(data, str):
        return json.loads(f.decrypt(bytes(data, 'utf8')))
    else:
        raise ValueError()

def release_keys(keys_dict, data_dict):
    sub_dict = {k: keys_dict[k] for k in data_dict.keys() if k != 'output'}
    return sub_dict