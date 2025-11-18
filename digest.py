import os
import datetime
from twarc import Twarc2
from jinja2 import Template
import requests

# 配置
bearer_token = os.environ["BEARER_TOKEN"]
username = os.environ["X_USERNAME"]
push_token = os.environ["PUSHPLUS_TOKEN"]

t = Twarc2(bearer_token=bearer_token)

# 时间范围：过去24小时
end_time = datetime.datetime.now(datetime.timezone.utc)
start_time = end_time - datetime.timedelta(days=1)

# 获取关注列表并抓取推文
following = list(t.following(username))
tweets = []

for user in following:
    user_id = user["id"]
    for tweet in t.timeline(user_id=user_id, start_time=start_time, end_time=end_time):
        tweets.append(tweet)

# 生成报告内容
if not tweets:
    content = f"<h2>{datetime.date.today()} 昨日您关注的账号无新推文</h2>"
else:
    # 简单按点赞数排序，取前50条
    tweets_sorted = sorted(tweets, key=lambda x: x["public_metrics"]["like_count"], reverse=True)[:50]
    with open("template.html", encoding="utf-8") as f:
        template = Template(f.read())
    content = template.render(date=datetime.date.today(), tweets=tweets_sorted, total=len(tweets))

# PushPlus 微信推送
requests.post(
    "http://www.pushplus.plus/send",
    json={
        "token": push_token,
        "title": f"{datetime.date.today()} X关注账号行业日报（{len(tweets)}条）",
        "content": content,
        "template": "html"
    },
)

print("微信推送成功")
