from ancile_core.decorators import transform_decorator, external_request_decorator
from ancile_web.errors import AncileException
from flask import current_app
import requests

name = 'rdl'


@external_request_decorator()
def rdl_fetch_usage(user=None, **kwargs):
    data = {'output': []}
    token = user['token']
    r = requests.get('https://localhost:9980/test/api/usage',
                     headers={'Authorization': f'Bearer {token}'})
    if r.status_code == 200:
        data.update(r.json())
    else:
        raise AncileException(f"Request error: {r.json()}")

    return data


@external_request_decorator()
def rdl_fetch_urls(user=None, **kwargs):
    data = {'output': []}
    token = user['token']
    r = requests.get('https://localhost:9980/test/api/urls',
                     headers={'Authorization': f'Bearer {token}'})
    if r.status_code == 200:
        data.update(r.json())
    else:
        raise AncileException(f"Request error: {r.json()}")

    return data


@external_request_decorator()
def rdl_fetch_youtube_search_history(user=None, **kwargs):
    data = {'output': []}
    token = user['token']
    r = requests.get('https://localhost:9980/test/api/youtube_search',
                     headers={'Authorization': f'Bearer {token}'})
    if r.status_code == 200:
        data.update(r.json())
    else:
        raise AncileException(f"Request error: {r.json()}")

    return data


@external_request_decorator()
def rdl_fetch_youtube_watch_history(user=None, **kwargs):
    data = {'output': []}
    token = user['token']
    r = requests.get('https://localhost:9980/test/api/youtube_watch',
                     headers={'Authorization': f'Bearer {token}'})
    if r.status_code == 200:
        data.update(r.json())
    else:
        raise AncileException(f"Request error: {r.json()}, token: {token}")

    return data


def aggregate_rdl_data(data_date_pairs, keep_raw_data):
    import pandas as pd
    import json
    from datetime import datetime

    df = pd.DataFrame(data_date_pairs, columns=['data', 'datetime'])
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    if keep_raw_data:
        df_grouped = df.set_index('datetime').groupby(['data', pd.Grouper(freq='D')]).size()
    else:
        df_grouped = df.set_index('datetime').groupby(pd.Grouper(freq='D')).count()
    df_grouped = df_grouped.rename(columns={'data': 'count'})
    result_obj_list = json.loads(df_grouped.to_json(orient='table'))['data']
    for d in result_obj_list:
        d['datetime'] = datetime.strptime(d['datetime'], '%Y-%m-%dT00:00:00.000Z').strftime('%a, %d %b %Y 00:00:00 GMT')
    if keep_raw_data:
        return result_obj_list
    else:
        results_flat_list = [[x['datetime'], x['count']] for x in result_obj_list]
        return results_flat_list


@transform_decorator
def rdl_group_usage_data_by_date(data):
    data_date_pairs = [(x[0], x[1]) for x in data['data']['usage']]
    results_flat_list = aggregate_rdl_data(data_date_pairs, False)
    data['output'].append('RDL Usage to Count By Date Transform.')

    # Delete raw data
    del data['data']
    data['data_searches_timeline'] = results_flat_list
    return data


@transform_decorator
def rdl_group_url_data_by_date(data):
    data_date_pairs = [(x[1], x[3]) for x in data['data']['urls']]
    results_flat_list = aggregate_rdl_data(data_date_pairs, False)
    data['output'].append('RDL URLs to Count By Date Transform.')
    # Delete raw data
    del data['data']
    data['data_urls_timeline'] = results_flat_list
    return data


@transform_decorator
def rdl_group_youtube_search_data_by_date(data):
    data_date_pairs = [(x['url'], x['time']) for x in data['data']]
    results_flat_list = aggregate_rdl_data(data_date_pairs, False)
    data['output'].append('RDL Youtube Search to Count By Date Transform.')
    # Delete raw data
    del data['data']
    data['data_youtube_search_timeline'] = results_flat_list
    return data


@transform_decorator
def rdl_group_youtube_watch_data_by_date(data):
    data_date_pairs = [(x['url'], x['time']) for x in data['data']]
    results_flat_list = aggregate_rdl_data(data_date_pairs, False)
    data['output'].append('RDL Youtube Watch to Count By Date Transform.')
    # Delete raw, unfiltered data
    del data['data']
    data['data_youtube_watch_timeline'] = results_flat_list
    return data


@transform_decorator
def rdl_group_usage_data_by_usage_date(data):
    data_date_pairs = [(x[0], x[1]) for x in data['data']['usage']]
    results_obj_list = aggregate_rdl_data(data_date_pairs, True)
    data['output'].append('RDL Usage to Count By Query and Date Transform.')
    # Delete raw data
    del data['data']
    data['data_usage_dates_count'] = results_obj_list
    return data


@transform_decorator
def rdl_group_url_data_by_url_date(data):
    data_date_pairs = [(x[0], x[3]) for x in data['data']['urls']]
    results_obj_list = aggregate_rdl_data(data_date_pairs, True)
    data['output'].append('RDL URLs to Count By URL and Date Transform.')
    # Delete raw data
    del data['data']
    data['data_urls_dates_count'] = results_obj_list
    return data


@transform_decorator
def rdl_group_youtube_search_data_by_query_date(data):
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
    new_str = searched_for_str.replace("Searched for ", "")
    return new_str


@transform_decorator
def rdl_group_youtube_watch_data_by_query_date(data):
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
    new_str = searched_for_str.replace("Watched ", "")
    return new_str


@transform_decorator
def rdl_political_filter(data):
    data['data'] = list(filter(obj_political_filter, data['data']))
    data['output'].append('Political filter applied.')


def obj_political_filter(raw_obj):
    political_terms = ['trump', 'clinton', 'putin', 'bernie', 'obama']
    for political_word in political_terms:
        if political_word in raw_obj['title'].lower():
            return False
    return True

# Note: Makes 6 calls to YouTube API for Speed Purposes Mostly
# There's sometimes an error when making 40-50 calls.
@transform_decorator
def rdl_categorize_youtube_watch_data(data):
    import requests
    import json
    import re

    id_list = []
    youtube_id_regex = '\?v=(.*)$'
    for ele in data['data']:
        id_list.append(re.search(youtube_id_regex, ele['url']).group(1))

    temp_id_list_for_query = []
    req_count = 0
    api_key = current_app.config['YOUTUBE_API_KEY']
    for iter_id in id_list:
        temp_id_list_for_query.append(iter_id)
        # Max of 50 YouTube Video IDs Per API Query
        if len(temp_id_list_for_query) == 50:
            cats = requests.get(
                'https://www.googleapis.com/youtube/v3/videos?key=' + api_key + '&part=snippet&id='
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
    import re
    youtube_id_regex = '\?v=(.*)$'
    return re.search(youtube_id_regex, url).group(1)


def join_category_ids_to_orig(rdl_data, response_json):
    for ele in response_json['items']:
        response_item_id = ele['id']
        rdl_data_ele = next((x for x in rdl_data['data'] if get_youtube_video_id(x['url']) == response_item_id), None)
        rdl_data_ele['categoryId'] = ele['snippet']['categoryId']


@transform_decorator
def rdl_group_youtube_watch_data_by_query_date_and_category(data):
    data_date_pairs = [(x['categoryId'], x['time']) for x in data['data']]
    results_obj_list = aggregate_rdl_data(data_date_pairs, True)
    data['output'].append('RDL Youtube Watched Videos to Count By Category ID and Date Transform.')
    # Delete raw data
    del data['data']
    data['data_youtube_watched_dates_count'] = results_obj_list
    return data
