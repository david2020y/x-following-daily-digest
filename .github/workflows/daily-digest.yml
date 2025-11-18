import os
import datetime
import pandas as pd
from twarc import Twarc2
from jinja2 import Template
import requests

bearer_token = os.environ['BEARER_TOKEN']
username = os.environ['X_USERNAME']
token = os.environ['PUSHPLUS_TOKEN']

t = Twarc2(bearer_token=bearer_token)
today = datetime.date.today().strftime("%Y-%m-%d")
yesterday = (datetime.date.today() - datetime.timedelta(days=1)

following = [u['id'] for u in t.following(username)]
tweets = []
for uid in following:
    for tweet in t.timeline(user_id=uid, start_time=yesterday):
        tweets.append(tweet)

if not tweets:
    content = f"【{today}】昨日您关注的账号无新推文"
else:
    df = pd.DataFrame(tweets)
    df['likes'] = df['public_metrics'].apply(lambda x: x['like_count'])
    df = df.sort_values('likes', ascending=False).head(40).reset_index(drop=True)

    with open('template.html') as f:
        template = Template(f.read())
    content = template.render(date=today, tweets=df.to_dict('records'), total=len(tweets))

requests.post("http://www.pushplus.plus/send", json={
    "token": token,
    "title": f"{today} X关注账号行业日报（{len(tweets)}条）",
    "content": content,
    "template": "html"
})
