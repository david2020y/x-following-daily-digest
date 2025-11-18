import os
import datetime
import pandas as pd
from twarc import Twarc2
from jinja2 import Template
import requests

bearer_token = os.environ['BEARER_TOKEN']
username = os.environ['X_USERNAME']
push_token = os.environ['PUSHPLUS_TOKEN']

t = Twarc2(bearer_token=bearer_token)

today = datetime.datetime.now().strftime("%Y-%m-%d")
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

# 获取关注列表
following_users = list(t.following(username))

tweets = []
for user in following_users:
    user_id = user['id']
    for tweet in t.timeline(user_id=user_id, start_time=yesterday):
        tweets.append(tweet)

if not tweets:
    content = f"<h2>{today} 昨日无新推文</h2>"
else:
    df = pd.DataFrame(tweets)
    df['likes'] = df['public_metrics'].apply(lambda x: x.get('like_count', 0))
    df = df.sort_values('likes', ascending=False).head(50)
    
    with open('template.html', encoding='utf-8') as f:
        template = Template(f.read())
    content = template.render(date=today, tweets=df.to_dict('records'), total=len(tweets))

# PushPlus 推送
requests.post("http://www.pushplus.plus/send", json={
    "token": push_token,
    "title": f"{today} X关注账号行业日报（{len(tweets)}条）",
    "content": content,
    "template": "html"
})
print("推送完成")
