import os
import datetime
import requests
from jinja2 import Template

bearer_token = os.environ["BEARER_TOKEN"]
username = os.environ["X_USERNAME"]
phone = os.environ["WHATSAPP_PHONE"]
apikey = os.environ["WHATSAPP_APIKEY"]

headers = {"authorization": f"Bearer {bearer_token}"}

# 获取用户 ID
user_resp = requests.get(f"https://api.twitter.com/2/users/by/username/{username}", headers=headers).json()
user_id = user_resp["data"]["id"]

# 获取 following 列表
following = requests.get(f"https://api.twitter.com/2/users/{user_id}/following?max_results=1000", headers=headers).json()

tweets = []
for user in following.get("data", []):
    user_timeline = requests.get(
        f"https://api.twitter.com/2/users/{user['id']}/tweets",
        params={"max_results": 100, "start_time": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).isoformat("T") + "Z"},
        headers=headers
    ).json()
    tweets.extend(user_timeline.get("data", []))

today = datetime.date.today().strftime("%Y-%m-%d")

if not tweets:
    text = f"*{today} X关注账号行业日报*\n\n昨日无新推文"
else:
    tweets = sorted(tweets, key=lambda x: x.get("public_metrics", {}).get("like_count", 0), reverse=True)[:30]
    lines = [f"*{today} X关注账号行业日报（共{len(tweets)}条）*\n"]
    for i, t in enumerate(tweets, 1):
        lines.append(f"{i}. @{t['author_id']} ❤️ {t['public_metrics']['like_count']}\n{t['text'][:150]}...\nhttps://x.com/i/status/{t['id']}\n")
    text = "\n".join(lines)

# WhatsApp 推送
url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&apikey={apikey}&text={requests.utils.quote(text)}"
requests.get(url)

print("WhatsApp 推送完成")
