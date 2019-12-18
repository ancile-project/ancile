from ancile.core.decorators import *
import logging
logger = logging.getLogger(__name__)


class Result:

    def __init__(self):
        self._dp_pair_data = list()
        self._stored_keys = dict()
        self._encrypted_data = dict()

    def __repr__(self):
        return f"<Result obj>"

    @UseDecorator()
    def return_to_app(self, data, encryption_keys, decrypt_field_list=None):

        if decrypt_field_list and isinstance(decrypt_field_list, list):
            dropped = set(encryption_keys.keys()) - set(decrypt_field_list)
            for key in dropped:
                del encryption_keys[key]
            data.update(**encryption_keys)
            self._dp_pair_data.append(data)
        else:
            self._dp_pair_data.append(data)
            encryption_keys.clear()
        return True


    def return_to_web(self, dpp):
        self._dp_pair_data.append(dpp)
        return True
