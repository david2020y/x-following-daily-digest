import os
import datetime
import json
import subprocess
from jinja2 import Template
import requests
import urllib.parse

username = os.environ["X_USERNAME"]
phone = os.environ["WHATSAPP_PHONE"]
apikey = os.environ["WHATSAPP_APIKEY"]

# 使用 snscrape 抓取昨日所有关注账号的推文
date_since = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
cmd = f"snscrape --jsonl --since {date_since} twitter-user-following {username}"

result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
tweets = [json.loads(line) for line in result.stdout.strip().split('\n') if line.strip()]

today = datetime.date.today().strftime("%Y-%m-%d")

if not tweets:
    text = f"{today} X关注账号行业日报\n\n昨日无新推文"
else:
    # 按点赞排序取前30条
    tweets = sorted(tweets, key=lambda x: x.get('likeCount', 0), reverse=True)[:30]
    
    with open("template.html", encoding="utf-8") as f:
        template = Template(f.read())
    html = template.render(date=today, tweets=tweets, total=len(tweets))
    
    # WhatsApp 最大支持 4096 字符，直接发 HTML 太长会截断，所以改成简洁文字版
    lines = [f"{today} X关注账号行业日报（共{len(tweets)}条）\n"]
    for i, t in enumerate(tweets, 1):
        user = t['user']['displayname'] or t['user']['username']
        text_preview = t['rawContent'].replace("\n", " ").replace("*", "").replace("_", "").replace("`", "")
        if len(text_preview) > 120:
            text_preview = text_preview[:120] + "..."
        line = f"{i}. @{t['user']['username']} ({user})\n❤ {t.get('likeCount',0)}   🔁 {t.get('retweetCount',0)}\n{text_preview}\nhttps://x.com/{t['user']['username']}/status/{t['id']}\n"
        lines.append(line)
    
    text = "\n".join(lines)

# 发送到 WhatsApp
url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&apikey={apikey}&text={urllib.parse.quote(text)}"
requests.get(url)

print("WhatsApp 推送成功")
