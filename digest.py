import os
import datetime
import pandas as pd
from twarc import Twarc2
from twarc_csv import CSVConverter
from jinja2 import Template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# 配置
bearer_token = os.environ['BEARER_TOKEN']
username = os.environ['X_USERNAME']
today = datetime.date.today()
since = today - datetime.timedelta(days=1)

t = Twarc2(bearer_token=bearer_token)

# 获取您关注的所有人（Following）
following = list(t.following(username))

# 抓取过去24小时推文
tweets = []
for user in following:
    for tweet in t.timeline(user['id'], start_time=since):
        tweets.append(tweet)

# 转换为DataFrame并简单过滤/排序
if tweets:
    df = pd.DataFrame(tweets)
    df = df.sort_values('public_metrics.like_count', ascending=False)

    # 生成HTML报告（可扩展为PDF）
    with open('template.html') as f:
        template = Template(f.read())
    html = template.render(date=today, tweets=df.to_dict('records')[:50])

    with open(f'report_{today}.html', 'w', encoding='utf-8') as f:
        f.write(html)

    # 发送邮件
    msg = MIMEMultipart()
    msg['From'] = os.environ['EMAIL_FROM']
    msg['To'] = os.environ['EMAIL_TO']
    msg['Subject'] = f"{today} X关注账号行业动态日报"

    msg.attach(MIMEText(html, 'html'))
    with open(f'report_{today}.html', 'rb') as f:
        part = MIMEApplication(f.read(), Name=f'report_{today}.html')
        part['Content-Disposition'] = f'attachment; filename="report_{today}.html"'
        msg.attach(part)

    server = smtplib.SMTP('smtp.qq.com' if 'qq' in os.environ['EMAIL_FROM'] else 'smtp.163.com', 465)
    server.login(os.environ['EMAIL_FROM'], os.environ['EMAIL_PASSWORD'])
    server.sendmail(os.environ['EMAIL_FROM'], os.environ['EMAIL_TO'], msg.as_string())
