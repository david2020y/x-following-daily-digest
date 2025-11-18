import os
import datetime
import traceback
from twarc import Twarc2
from jinja2 import Template
import requests

try:
    bearer_token = os.environ["BEARER_TOKEN"]
    username = os.environ["X_USERNAME"]
    push_token = os.environ["PUSHPLUS_TOKEN"]

    print("初始化 Twarc2...")
    t = Twarc2(bearer_token=bearer_token)

    # 时间范围：过去24小时（UTC）
    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(hours=30)  # 多抓6小时避免时区问题

    print(f"正在获取 @{username} 的关注列表...")
    following = list(t.following(username))
    print(f"成功获取 {len(following)} 个关注账号")

    tweets = []
    for user in following:
        user_id = user["id"]
        try:
            for tweet in t.timeline(user_id=user_id, start_time=start_time, end_time=end_time, max_results=100):
                tweets.append(tweet)
        except Exception as e:
            print(f"抓取 {user['username']} 时出错: {str(e)}")

    print(f"共抓取到 {len(tweets)} 条推文")

    # 生成报告
    if not tweets:
        content = "<h2>昨日您关注的账号无新推文</h2><p>可能原因：时区差异或确无更新</p>"
    else:
        tweets_sorted = sorted(tweets, key=lambda x: x["public_metrics"]["like_count"], reverse=True)[:50]
        with open("template.html", encoding="utf-8") as f:
            template = Template(f.read())
        content = template.render(date=datetime.date.today(), tweets=tweets_sorted, total=len(tweets))

    # 微信推送
    r = requests.post(
        "http://www.pushplus.plus/send",
        json={
            "token": push_token,
            "title": f"{datetime.date.today()} X关注账号行业日报（{len(tweets)}条）",
            "content": content,
            "template": "html"
        },
        timeout=30
    )
    print(f"推送返回: {r.text}")

except Exception as e:
    error_msg = f"<h3>日报生成失败</h3><pre>{traceback.format_exc()}</pre>"
    requests.post(
        "http://www.pushplus.plus/send",
        json={
            "token": push_token,
            "title": "X日报系统错误通知",
            "content": error_msg,
            "template": "html"
        }
    )
    raise e
