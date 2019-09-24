
from ancile_core.decorators import transform_decorator, external_request_decorator
from ancile_web.errors import AncileException
from flask import current_app
import requests
from ancile_core.functions.general import get_token

name = 'rdl'


@external_request_decorator()
def rdl_fetch(user=None, url='https://localhost:9980', api_to_fetch=None, username=None,  **kwargs):
    """
    Fetches Web Search Data From RDL
    :param username:
    :param user:
    :param url:
    :param kwargs:
    :param api_to_fetch
    :return:
    """
    data = {'output': []}
    token = get_token(user)
    params = {'username':username}
    r = requests.get(f'{url}/test/api/{api_to_fetch}', headers={'Authorization': f'Bearer {token}'}, params=params)

    if r.status_code == 200:
        data.update(r.json())
    else:
        raise AncileException(f"Request error: {r.json()}")
    return data


def aggregate_rdl_data(data_date_pairs, keep_raw_data):
    """
    Aggregates data from RDL either by date or by date + data (e.g. url, search query, etc)
    :param data_date_pairs:
    :param keep_raw_data:
    :return:
    """
    import pandas as pd
    import json
    from datetime import datetime

    df = pd.DataFrame(data_date_pairs, columns=['data', 'datetime'])
    df['datetime'] = pd.to_datetime(df['datetime'], format="%a, %d %b %Y %H:%M:%S GMT")
    if keep_raw_data:
        df_grouped = df.set_index('datetime').groupby(['data', pd.Grouper(freq='D')]).size()
    else:
        df_grouped = df.set_index('datetime').groupby(pd.Grouper(freq='D')).count()
    df_grouped = df_grouped.rename(columns={'data': 'count'})
    result_obj_list = json.loads(df_grouped.to_json(orient='table'))['data']
    for d in result_obj_list:
        d['datetime'] = datetime.strptime(d['datetime'], '%Y-%m-%dT%H:%M:%S.000Z').strftime('%a, %d %b %Y 00:00:00 GMT')

    if keep_raw_data:
        return result_obj_list
    else:
        results_flat_list = [[x['datetime'], x['count']] for x in result_obj_list]
        return results_flat_list


@transform_decorator
def rdl_group_usage_data_by_date(data, whole_word="False", query = ""):
    """
    Aggregates web searches by day (e.g. 1/1/2017 : 1, 1/1/2018 : 10)
    :param data:
    :return:
    """
    import re
    from urllib.parse import unquote
    from functools import reduce
    filtered_data = data['data']['usage']

    if query:
        query = unquote(query)
        if whole_word == 'true':
            # Make sure the searches equal the user defined search term
            # Or that the user defined search term is surrounded by spaces
            # Data
            filter_regex = '(^|[^\w])%s($|[^\w])' % query
            filtered_data = list(filter(lambda x: re.search(filter_regex, x[0]), filtered_data))
        else:
            filtered_data = list(filter(lambda x: query in x[0], filtered_data))

    data_date_pairs = [(x[0], x[1]) for x in filtered_data]
    results_flat_list = aggregate_rdl_data(data_date_pairs, False)
    data['output'].append('RDL Usage to Count By Date Transform.')
    data['searches'] = {}
    data['searches']['timeline'] = results_flat_list
    data['searches']['global_extents'] = {
        'min': data['data']['extents']['min'],
        'max': data['data']['extents']['max']
    }
    data['searches']['total'] = reduce(lambda x, y: x + y[1], results_flat_list, 0)

    # Delete raw data
    del data['data']
    return data


def lookup(s):
    import pandas as pd
    dates = {date: pd.to_datetime(date) for date in s}
    return list(map(lambda x: dates[x], s))


@transform_decorator
def rdl_usage_date_passthrough(data, whole_word="False", query=""):
    """
    Returns a list of queries and dates
    :param query:
    :param whole_word:
    :param data:
    :return:
    """
    from dateutil.parser import parse as parse_date
    import re
    from urllib.parse import unquote
    filtered_data = data['data']['usage']
    if query:
        query = unquote(query)
        if whole_word == 'true':
            # Make sure the searches equal the user defined search term
            # Or that the user defined search term is surrounded by spaces
            # Data
            filter_regex = '(^|[^\w])%s($|[^\w])' % query
            filtered_data = list(filter(lambda x: re.search(filter_regex, x[0]), filtered_data))
        else:
            filtered_data = list(filter(lambda x: query in x[0], filtered_data))

    filtered_data.reverse()
    filtered_data_objs = []
    count = 1
    for datapoint in filtered_data:
        filtered_data_objs.append({'id' : count, 'query_text': datapoint[0], 'timestamp': datapoint[1]})
        count += 1

    data['output'].append('RDL Usage and Date Passthrough.')
    data['data'] = filtered_data_objs
    return data


@transform_decorator
def rdl_urls_date_passthrough(data, query=""):
    """
    Returns a list of queries and dates
    :param query:
    :param whole_word:
    :param data:
    :return:
    """
    from dateutil.parser import parse as parse_date
    import re
    from urllib.parse import unquote
    filtered_data = data['data']['urls']
    if query:
        query = unquote(query)
        filtered_data = list(filter(lambda x: query in x[1], filtered_data))

    # filtered_data.reverse()
    filtered_data_objs = []
    count = 1
    for datapoint in filtered_data:
        filtered_data_objs.append({'id': count, 'url': datapoint[1], 'timestamp': datapoint[3]})
        count += 1

    data['output'].append('RDL Url and Date Passthrough.')
    data['data'] = filtered_data_objs
    return data


@transform_decorator
def rdl_usage_data_freq(data, min_date="", max_date=""):
    """
    Returns top 10 words in frequency from google searches within date ranges
    :param max_date:
    :param min_date:
    :param data:
    :return:
    """
    from dateutil.parser import parse as parse_date
    from collections import Counter

    filtered_data = data['data']['usage']
    if min_date and min_date != 'null' and min_date !='Invalid Date':
        index_of_open_paren = min_date.index('(')
        min_date_obj = parse_date(min_date[:index_of_open_paren - 1])
        filtered_data = list(filter(lambda x: parse_date(x[1]) >= min_date_obj, filtered_data))

    if max_date and max_date != 'null' and max_date !='Invalid Date':
        index_of_open_paren = max_date.index('(')
        max_date_obj = parse_date(max_date[:index_of_open_paren - 1])
        filtered_data = list(filter(lambda x: parse_date(x[1]) <= max_date_obj, filtered_data))

    word_list = ''
    word_list += ' '.join(x[0] for x in filtered_data)
    word_list = word_list.split(' ')
    Counter = Counter(word_list)
    most_freq = Counter.most_common(10)
    most_freq_obj_list = []
    for x in most_freq:
        most_freq_obj_list.append({'word': x[0], 'count': x[1]})
    data['output'].append('RDL Top Ten Frequency Words Transform.')
    data['freqwords'] = most_freq_obj_list
    # Delete raw data
    del data['data']
    return data


@transform_decorator
def rdl_usage_data_recurrence(data):
    """
    Returns top 10 words in frequency from google searches within date ranges
    :param data:
    :return:
    """
    from datetime import  timedelta
    from dateutil.parser import parse as parse_date
    import nltk
    nltk.download('wordnet')
    nltk.download('stopwords')
    from nltk.stem import WordNetLemmatizer
    from nltk.corpus import stopwords
    stops = set(stopwords.words("english"))
    filtered_data = data['data']['usage']
    lemmatizer = WordNetLemmatizer()

    word_week_dict = {}  # Words to weeks
    for search_term in filtered_data:
        dt = parse_date(search_term[1]).date()
        week_dt = dt - timedelta(days=dt.weekday())  # Get Sunday
        word_list = search_term[0].split(' ')
        for word in word_list:
            lem_word = lemmatizer.lemmatize(word)
            if lem_word in stops:
                continue
            if lem_word in word_week_dict:
                word_week_dict[lem_word].add(week_dt)
            else:
                word_week_dict[lem_word] = {week_dt}

    # Get Minimum and Maximum weeks
    total_weeks = 1
    if data['data']['extents']['min'] is not None and data['data']['extents']['max'] is not None:
        dt = parse_date(data['data']['extents']['min'])
        dt = dt - timedelta(days=dt.weekday())  # Get Sunday
        dt = dt.date()  # Truncate to date
        end = parse_date(data['data']['extents']['max'])
        end = end - timedelta(days=end.weekday())
        end = end.date()
        total_weeks = (end - dt).days / 7
        if total_weeks == 0:
            total_weeks = 1

    word_recurrences = []
    for word in word_week_dict:
        word_recurrences.append({'lemma': word, 'recurrence': len(word_week_dict[word]) / total_weeks})
    word_recurrences.sort(reverse=True, key=lambda x: x['recurrence'])
    top_ten = word_recurrences[:10]
    data['output'].append('RDL Top Ten Recurrence Words Transform.')
    data['items'] = top_ten
    # Delete raw data
    del data['data']
    return data


@transform_decorator
def rdl_group_url_data_by_date(data, query=""):
    """
    Aggregates urls visited by day (e.g. 1/1/2017 : 1, 1/1/2018 : 10)
    :param query:
    :param data:
    :return:
    """
    from dateutil.parser import parse as parse_date
    from urllib.parse import unquote
    from functools import reduce

    filtered_data = data['data']['urls']
    if query:
        query = unquote(query)
        filtered_data = list(filter(lambda x: query in x[1], filtered_data))
    data_date_pairs = [(x[1], x[3]) for x in filtered_data]
    results_flat_list = aggregate_rdl_data(data_date_pairs, False)
    data['output'].append('RDL Urls to Count By Date Transform.')
    data['searches'] = {}
    data['searches']['timeline'] = results_flat_list
    data['searches']['global_extents'] = {}
    data['searches']['global_extents']['min'] = data['data']['extents']['min']
    data['searches']['global_extents']['max'] = data['data']['extents']['max']
    data['searches']['total'] = reduce(lambda x, y: x + y[1], results_flat_list, 0)
    # Delete raw data
    del data['data']


@transform_decorator
def rdl_url_data_recurrence(data):
    """
    Returns top 10 url in frequency from chrome searches within date ranges
    :param data:
    :return:
    """
    from datetime import timedelta
    from dateutil.parser import parse as parse_date
    from urllib.parse import urlparse
    filtered_data = data['data']['urls']

    url_week_dict = {}  # urls to weeks
    for url_visit in filtered_data:
        dt = parse_date(url_visit[3]).date()
        week_dt = dt - timedelta(days=dt.weekday())  # Get Sunday
        parsed_uri = urlparse(url_visit[1])
        if parsed_uri.scheme not in ['http', 'https']:
            continue
        uri_host = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        if uri_host in url_week_dict:
            url_week_dict[uri_host].add(week_dt)
        else:
            url_week_dict[uri_host] = {week_dt}
    # print(filtered_data)
    # Get Minimum and Maximum weeks
    total_weeks = 1
    if data['data']['extents']['min'] is not None and data['data']['extents']['max'] is not None:
        dt = parse_date(data['data']['extents']['min'])
        dt = dt - timedelta(days=dt.weekday())  # Get Sunday
        dt = dt.date()  # Truncate to date

        end = parse_date(data['data']['extents']['max'])
        end = end - timedelta(days=end.weekday())
        end = end.date()

        total_weeks = (end - dt).days / 7
        if total_weeks == 0:
            total_weeks = 1

    url_recurrences = []
    for url in url_week_dict:
        url_recurrences.append({'hostname': url, 'recurrence': len(url_week_dict[url]) / total_weeks})
    url_recurrences.sort(reverse=True, key=lambda x: x['recurrence'])
    top_fifteen = url_recurrences[:15]
    data['output'].append('RDL Top Fifteen Recurrence URLs Transform.')
    data['items'] = top_fifteen
    # Delete raw data
    del data['data']
    return data



@transform_decorator
def rdl_group_youtube_search_data_by_date(data):
    """
    Aggregates YouTube searches by day (e.g. 1/1/2017 : 1, 1/1/2018 : 10)
    :param data:
    :return:
    """
    data_date_pairs = [(x['url'], x['time']) for x in data['data']]
    results_flat_list = aggregate_rdl_data(data_date_pairs, False)
    data['output'].append('RDL Youtube Search to Count By Date Transform.')
    # Delete raw data
    del data['data']
    data['data_youtube_search_timeline'] = results_flat_list
    return data


@transform_decorator
def rdl_group_youtube_watch_data_by_date(data):
    """
    Aggregates YouTube Watched Videos by Day (e.g. 1/1/2017 : 1, 1/1/2018 : 10)
    :param data:
    :return:
    """
    data_date_pairs = [(x['url'], x['time']) for x in data['data']]
    results_flat_list = aggregate_rdl_data(data_date_pairs, False)
    data['output'].append('RDL Youtube Watch to Count By Date Transform.')
    # Delete raw, unfiltered data
    del data['data']
    data['data_youtube_watch_timeline'] = results_flat_list
    return data


@transform_decorator
def rdl_group_location_data_by_date(data, xmin=None, xmax=None, ymin=None, ymax=None):
    """
    Aggregates Location Data by Day (e.g. 1/1/2017 : 1, 1/1/2018 : 10)
    :param data:
    :param xmin: x/y min/max refer to the bounding square on locations to return
    :param xmax:
    :param ymin:
    :param ymax:
    :return:
    """
    from functools import reduce
    from dateutil.parser import parse as parse_date
    filtered_data = data
    filtered_locs = filtered_data['data']['locations']

    if xmin and xmin != 'null':
        filtered_locs = list(filter(lambda x: x[0][1] >= float(xmin), filtered_locs))
    if xmax and xmax != 'null':
        filtered_locs = list(filter(lambda x: x[0][1] <= float(xmax), filtered_locs))
    if ymin and ymin != 'null':
        filtered_locs = list(filter(lambda x: x[0][0] >= float(ymin), filtered_locs))
    if ymax and ymax != 'null':
        filtered_locs = list(filter(lambda x: x[0][0] <= float(ymax), filtered_locs))

    filtered_data['data']['locations'] = filtered_locs

    data_date_pairs = [(x[0], x[1]) for x in filtered_data['data']['locations']]
    results_flat_list = aggregate_rdl_data(data_date_pairs, False)
    data['locations'] = {}
    data['locations']['timeline'] = results_flat_list
    data['locations']['global_extents'] = {
        'min': filtered_data['data']['extents']['min'],
        'max': filtered_data['data']['extents']['max']
    }
    data['locations']['total'] = reduce(lambda x, y: x + y[1], results_flat_list, 0)
    data['output'].append('RDL Location to Count By Date Transform.')
    # Delete raw, unfiltered data
    del data['data']
    return data


@transform_decorator
def rdl_group_location_data_by_location_with_date_limits(data, min_date=None, max_date=None):
    """
    Aggregates Location Data by Location
    :param data:
    :param min_date:
    :param max_date:
    :return:
    """
    from functools import reduce
    from dateutil.parser import parse as parse_date
    filtered_data = data['data']['locations']
    if min_date and min_date != 'null' and min_date != 'Invalid Date':
        index_of_open_paren = min_date.index('(')
        min_date = parse_date(min_date[:index_of_open_paren - 1])
        filtered_data = list(filter(lambda x: parse_date(x[1]) >= min_date, filtered_data))
    if max_date and max_date != 'null' and max_date != 'Invalid Date':
        index_of_open_paren = max_date.index('(')
        max_date = parse_date(max_date[:index_of_open_paren - 1])
        filtered_data = list(filter(lambda x: parse_date(x[1]) <= max_date, filtered_data))

    # Now go from [[lat,lng], datetime] to [[lat,lng], count]
    grouped_data = []
    for ele in filtered_data:
        lat_lng_already_exist = any(ele[0] in sublist for sublist in grouped_data)
        if not lat_lng_already_exist:
            grouped_data.append([ele[0], 1])
        else:
            # Increment existing count
            existing_ele = next((x for x in grouped_data if x[0] == ele[0]), None)
            existing_ele[1] = existing_ele[1] + 1

    # # Sort grouped data by count desc
    # grouped_data.sort(key=lambda x: x[1], reverse=True)

    data['output'].append('RDL Location Group By Location Transform.')
    # Delete raw, unfiltered data
    del data['data']
    data['locations'] = {}
    data['locations']['points'] = grouped_data
    data['locations']['total'] = reduce(lambda x, y: x + y[1], grouped_data, 0)
    return data


def rdl_group_usage_data_by_usage_date(data):
    """
    Aggregates web searches by day and search query. E.g. {"how many boats are in the US Navy", 1/1/2017, 4}
    :param data:
    :return:
    """
    data_date_pairs = [(x[0], x[1]) for x in data['data']['usage']]
    results_obj_list = aggregate_rdl_data(data_date_pairs, True)
    data['output'].append('RDL Usage to Count By Query and Date Transform.')
    # Delete raw data
    del data['data']
    data['data_usage_dates_count'] = results_obj_list
    return data


@transform_decorator
def rdl_group_url_data_by_url_date(data):
    """
    Aggregates urls visited by day and url. E.g. {"www.google.com", 1/1/2018, 20}
    :param data:
    :return:
    """
    data_date_pairs = [(x[0], x[3]) for x in data['data']['urls']]
    results_obj_list = aggregate_rdl_data(data_date_pairs, True)
    data['output'].append('RDL URLs to Count By URL and Date Transform.')
    # Delete raw data
    del data['data']
    data['data_urls_dates_count'] = results_obj_list
    return data


@transform_decorator
def rdl_group_youtube_search_data_by_query_date(data):
    """
    Aggregates YouTube searches by day and search query e.g. {"funny videos", 1/1/2017, 8}
    :param data:
    :return:
    """
    for x in data['data']:
        x['title'] = delete_searched_for(x['title'])
    data_date_pairs = [(x['title'], x['time']) for x in data['data']]
    results_obj_list = aggregate_rdl_data(data_date_pairs, True)
    data['output'].append('RDL Youtube Searches to Count By URL and Date Transform.')
    # Delete raw, unfiltered urls from data
    del data['data']
    data['data_youtube_searches_dates_count'] = results_obj_list
    return data


def delete_searched_for(searched_for_str):
    """
    Deletes the "Searched for" prefix that comes with all YouTube search queries.
    :param searched_for_str:
    :return:
    """
    new_str = searched_for_str.replace("Searched for ", "")
    return new_str


@transform_decorator
def rdl_group_youtube_watch_data_by_query_date(data):
    """
    Aggregates YouTube Watched videos by date and video title. e.g. {"Top 10 Funniest Moments in Airplane", 1/1/2019, 8}
    :param data:
    :return:
    """
    for x in data['data']:
        x['title'] = delete_watched(x['title'])
    data_date_pairs = [(x['title'], x['time']) for x in data['data']]
    results_obj_list = aggregate_rdl_data(data_date_pairs, True)
    data['output'].append('RDL Youtube Watched Videos to Count By URL and Date Transform.')
    # Delete raw data
    del data['data']
    data['data_youtube_watched_dates_count'] = results_obj_list
    return data


def delete_watched(searched_for_str):
    """
    Deletes the "Watched " prefix that comes with YouTube watched history data.
    :param searched_for_str:
    :return:
    """
    new_str = searched_for_str.replace("Watched ", "")
    return new_str


@transform_decorator
def rdl_political_filter(data):
    """
    Filters out a few political words from data dictionary
    :param data:
    :return:
    """
    data['data'] = list(filter(obj_political_filter, data['data']))
    data['output'].append('Political filter applied.')


def obj_political_filter(raw_obj):
    """
    Filters out names of key political figures from the title element of a dict
    :param raw_obj:
    :return:
    """
    political_terms = ['trump', 'clinton', 'putin', 'bernie', 'obama']
    for political_word in political_terms:
        if political_word in raw_obj['title'].lower():
            return False
    return True

# Note: Makes 6 calls to YouTube API for Speed Purposes Mostly
# There's sometimes an error when making 40-50 calls.
@transform_decorator
def rdl_categorize_youtube_watch_data(data, youtube_api_key):
    """
    Categorizes YouTube Watched videos using YouTubes category API
    Adds in the categories to original data
    :param data:
    :return:
    """
    import requests
    import json
    import re

    id_list = []
    youtube_id_regex = '\?v=(.*)$'
    for ele in data['data']:
        id_list.append(re.search(youtube_id_regex, ele['url']).group(1))

    temp_id_list_for_query = []
    req_count = 0
    for iter_id in id_list:
        temp_id_list_for_query.append(iter_id)
        # Max of 50 YouTube Video IDs Per API Query
        if len(temp_id_list_for_query) == 50:
            cats = requests.get(
                'https://www.googleapis.com/youtube/v3/videos?key=' + youtube_api_key + '&part=snippet&id='
                + ','.join(temp_id_list_for_query), verify=False)
            response_json = json.loads(cats.text)
            join_category_ids_to_orig(data, response_json)
            temp_id_list_for_query = []
            req_count = req_count + 1
            if req_count == 6:
                break

    for ele in data['data']:
        if 'categoryId' not in ele:
            ele['categoryId'] = '-1'

    data['output'].append('RDL Youtube Watched Videos Categorized.')

    return data


def get_youtube_video_id(url):
    """
    Parses out YouTube Video IDs from URLs
    :param url:
    :return:
    """
    import re
    youtube_id_regex = '\?v=(.*)$'
    return re.search(youtube_id_regex, url).group(1)


def join_category_ids_to_orig(rdl_data, response_json):
    """
    Adds in a YouTube video category id to the original RDL data
    :param rdl_data:
    :param response_json:
    :return:
    """
    for ele in response_json['items']:
        response_item_id = ele['id']
        rdl_data_ele = next((x for x in rdl_data['data'] if get_youtube_video_id(x['url']) == response_item_id), None)
        rdl_data_ele['categoryId'] = ele['snippet']['categoryId']


@transform_decorator
def rdl_group_youtube_watch_data_by_query_date_and_category(data):
    """
    Groups RDL data By Video Category
    :param data:
    :return:
    """
    data_date_pairs = [(x['categoryId'], x['time']) for x in data['data']]
    results_obj_list = aggregate_rdl_data(data_date_pairs, True)
    data['output'].append('RDL Youtube Watched Videos to Count By Category ID and Date Transform.')
    # Delete raw data
    del data['data']
    data['data_youtube_watched_dates_count'] = results_obj_list
    return data


