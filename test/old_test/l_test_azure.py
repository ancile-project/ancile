import requests
import json

js = {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzYWx0IjoiXFx4MjQzMjYyMjQzMTMyMjQ3NDMwNGI0NTQxNjU0ZDM3NGQ2ZjcyNzc2NDcwNmQ3YTQzNjQ1Mjc4NWE3NSJ9.4LA3PuPML2-1eaYwaX9JN8kTIJhUA31FZgQxqRIW4p4",
    "users": ["user"],
    "purpose": "research",
    "program": """
# dp_1 = azure.get_available_rooms(user=user("user"), floor=3)
dp_1 = azure.book_room(user=user("user"), room=375)

result.append_dp_data_to_result(data=dp_1)
    """
}

res = requests.post('https://dev.ancile.smalldata.io/api/run', json=js)

print(res.status_code)
new_js = res.json()
if new_js.get('result', False) == 'error':
    print(new_js['traceback'])
else:
    print(json.dumps(new_js, indent=4))
