import os
import datetime
import json
import subprocess
from jinja2 import Template
import requests

username = os.environ["X_USERNAME"]
push_token = os.environ["PUSHPLUS_TOKEN"]

# 使用 snscrape 抓取过去24小时推文
date_since = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
cmd = f"snscrape --jsonl --since {date_since} twitter-user-following {username}"

result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

tweets = []
for line in result.stdout.strip().split('\n'):
    if line.strip():
        tweets.append(json.loads(line))

print(f"抓取到 {len(tweets)} 条推文")

if not tweets:
    content = f"<h2>{datetime.date.today()} 昨日关注账号无新推文</h2>"
else:
    tweets_sorted = sorted(tweets, key=lambda x: x['likeCount'], reverse=True)[:50]
    with open("template.html", encoding="utf-8") as f:
        template = Template(f.read())
    content = template.render(date=datetime.date.today(), tweets=tweets_sorted, total=len(tweets))

requests.post("http://www.pushplus.plus/send", json={
    "token": push_token,
    "title": f"{datetime.date.today()} X关注账号行业日报（{len(tweets)}条）",
    "content": content,
    "template": "html"
})
