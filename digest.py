import os
import datetime
import requests
import urllib.parse

bearer_token = os.environ["BEARER_TOKEN"]
username = os.environ["X_USERNAME"]
phone = os.environ["WHATSAPP_PHONE"]
apikey = os.environ["WHATSAPP_APIKEY"]

headers = {"Authorization": f"Bearer {bearer_token}"}

# 1. 获取自己的 user_id
me = requests.get(f"https://api.twitter.com/2/users/by/username/{username}", headers=headers).json()
my_id = me["data"]["id"]

# 2. 获取 following 列表（最多1000人）
following = []
next_token = None
while True:
    url = f"https://api.twitter.com/2/users/{my_id}/following?max_results=1000"
    if next_token:
        url += f"&pagination_token={next_token}"
    resp = requests.get(url, headers=headers).json()
    following.extend(resp.get("data", []))
    next_token = resp.get("meta", {}).get("next_token")
    if not next_token:
        break

# 3. 抓取昨天的推文
tweets = []
start_time = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).isoformat("T") + "Z"

for user in following:
    user_id = user["id"]
    timeline_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    params = {"max_results": 100, "start_time": start_time, "tweet.fields": "public_metrics,created_at"}
    resp = requests.get(timeline_url, headers=headers, params=params).json()
    tweets.extend(resp.get("data", []))

today = datetime.date.today().strftime("%Y-%m-%d")

if not tweets:
    text = f"*{today} X关注账号行业日报*\n\n昨日无新推文（或关注人数过多，仅展示部分）"
else:
    tweets = sorted(tweets, key=lambda x: x["public_metrics"]["like_count"], reverse=True)[:30]
    lines = [f"*{today} X关注账号行业日报（共{len(tweets)}条）*\n"]
    for i, t in enumerate(tweets, 1):
        lines.append(f"{i}. {t['text'][:140].replace(chr(10), ' ')}...\n❤️ {t['public_metrics']['like_count']}   🔗 https://x.com/i/status/{t['id']}\n")
    text = "\n".join(lines)

# WhatsApp 推送
url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&apikey={apikey}&text={urllib.parse.quote(text)}"
requests.get(url, timeout=30)

print("WhatsApp 推送成功")
