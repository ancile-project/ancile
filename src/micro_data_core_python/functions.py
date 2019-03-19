from src.micro_data_core_python.user_specific import UserSpecific
from src.micro_data_core_python.datapolicypair import DataPolicyPair

class AncileException(Exception):
    pass

## ALLOWED is probably not needed
class Allowed:
    pass

class Transformation(Allowed):
    @staticmethod
    @UserSpecific.transform_decorator
    def asdf(data):
        data['asdf'] = True
        print('FUNC: asdf')
        return True

    @staticmethod
    @UserSpecific.transform_decorator
    def qwer(data):
        data['qwer'] = True
        print('FUNC: qwer')
        return True

    @staticmethod
    @UserSpecific.transform_decorator
    def zxcv(data):
        data['qwer'] = True
        print('FUNC: zxcv')
        return True

    @staticmethod
    @UserSpecific.transform_decorator
    def filter_floor(floor):
        print("FUNC: filter_floor" + str(floor))
        return True

    @staticmethod
    @UserSpecific.transform_decorator
    def keep_keys(data, keys = []):
        dropped = set(data.keys()) - set(keys)
        for key in dropped:
            del data[key] 
        return True


    
class DataIngress(Allowed):

    @staticmethod
    def get_empty_data_pair(data_source=None):
        ## PROBABLY NEED TO CHANGE TO TAKE A USER INFO ARGUMENT
        return DataPolicyPair(UserSpecific._user_policies[data_source])


    @staticmethod
    @UserSpecific.get_data_decorator
    def fetch_test_data(data=None, data_source="dataA", token=None):
        print("FUNC: fetch_test_data")
        data['fetch_test_data'] = True
        return True

    @staticmethod
    @UserSpecific.get_data_decorator
    def get_data(data, target_url=None, token=None, data_source=None):
        import requests
        print("FUNC: GET_DATA")
        print("  target_url: " + target_url)
        # _, access_token = _url_preprocessor(target_url, UserSpecific._user_tokens)
        # access_token = str(access_token, 'utf8')

        r = requests.get(target_url, headers={'Authorization': "Bearer " + token})

        if r.status_code == 200:
            data.update(r.json()) # Need to maintain given dict
        else:
            print(r.status_code)
            raise AncileException("Request error")

class DataEgress(Allowed):
    @staticmethod
    @UserSpecific.return_data_decorator
    def return_data(data):
        print(f'FUNC: return. data: {data}')
        return data


def _url_preprocessor(target_url, sensitive_data):
    """
    A helper function that searches sensitive_data 
    for a url that matches or is a superstring of the target url
    it returns this record
    """
    import urllib.parse

    def remove_prefix(instring):
        """
        A helper function that removes a leading www. from 
        a given url. 

        NOTE: will error if the string is exactly www.
        This shouldn't happen but might be worth thinking
        about, if our abstractions around data change
        """
        instring = instring.strip()
        if instring == "www.":
            raise AncileException("Invalid URL from configs")
        elif instring.startswith("www."):
            return instring[4:]
        else: 
            return instring

    target_base = remove_prefix(urllib.parse.urlparse(target_url).netloc)
    for record in sensitive_data:
        record_base = remove_prefix(str(urllib.parse.urlparse(record[0]).netloc, 'utf8'))
        # if record_base == target_base:
        # Want to handle situations where site url might not
        # be the same as api urls:
        #  ex: github.com vs api.github.com
        # this may or may not be a problem based on the config
        if target_base in record_base:
            return record

    raise AncileException("No corresponding data token")