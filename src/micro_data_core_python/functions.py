from src.micro_data_core_python.policy_processor import PolicyProcessor

class AncileException(Exception):
    pass


@PolicyProcessor.decorator
def asdf():
    print('FUNC: asdf')


@PolicyProcessor.decorator
def qwer():
    print('FUNC: qwer')


@PolicyProcessor.decorator
def zxcv():
    print('FUNC: zxcv')


@PolicyProcessor.decorator
def get_location():
    print("FUNC: get_location")
    return True


@PolicyProcessor.decorator
def filter_floor(floor):
    print("FUNC: filter_floor" + str(floor))
    return True

@PolicyProcessor.decorator
def get_data(target_url, sensitive_data):
    import requests
    print("FUNC: GET_DATA")
    print("  target_url: " + target_url)
    _, access_token = _url_preprocessor(target_url, sensitive_data)
    access_token = str(access_token, 'utf8')

    r = requests.get(target_url, headers={'Authorization': "Bearer " + access_token})
#     print(r.status_code)
    # print(r.json())
    try:
        return r.json()
    except ValueError:
        return r.text


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