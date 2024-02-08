import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re

# 设置天气信息获取的API链接
weather_api_url = 'https://v2.api-m.com/api/weather?city=%E6%B2%B3%E5%8D%97%E7%9C%81%E9%A9%BB%E9%A9%AC%E5%BA%97%E5%B8%82%E6%B1%9D%E5%8D%97%E5%8E%BF'
# 设置每日一言获取的API链接
quote_api_url = 'https://api.mu-jie.cc/stray-birds/range?type=json'
# 设置包含收件人邮箱地址的文本文件的URL
recipient_url = ''

# 获取收件人邮箱地址
recipient_response = requests.get(recipient_url)

if recipient_response.status_code == 200:
    recipient_emails = recipient_response.text.strip().split('\n')  # 按行切割邮箱地址
else:
    print(f"获取收件人邮箱失败，错误代码: {recipient_response.status_code}, 错误信息: {recipient_response.text}")
    exit()

# 获取天气信息
weather_response = requests.get(weather_api_url)

# 检查天气响应是否成功
if weather_response.status_code == 200:
    weather_data = weather_response.json()

    city = weather_data['data']['city']
    forecast = weather_data['data']['data']

    # 获取每日一言
    quote_response = requests.get(quote_api_url)
    if quote_response.status_code == 200:
        quote_data = quote_response.json()
        chinese_quote = quote_data['cn']

        # 设置邮件服务器和邮箱信息
        smtp_server = 'smtp.qq.com'
        smtp_port = 587
        sender_email = ''  # 替换为你的 QQ 邮箱地址
        sender_password = ''  # 替换为你的 QQ 邮箱授权码

        # 构建邮件内容
        email_content = f"城市: {city}\n\n天气预报:\n"

        # 仅保留第二和第三条天气预报数据
        for index, day in enumerate(forecast[1:3], start=1):
            date = day['date']
            temperature = day['temperature']
            weather_desc = day['weather']
            wind = day['wind']
            air_quality = day['air_quality']

            # 添加"明天"或"今天"前缀
            if index == 1:
                email_content += "今天："
            elif index == 2:
                email_content += "明天："

            email_content += f'{date}: 温度:{temperature}, 天气:{weather_desc}, 风力:{wind}, 空气质量:{air_quality}\n'

            # 检查天气描述是否包含"雨"关键词
            if '雨' in weather_desc:
                email_content += f'{date}有雨，请带伞\n'

        # 添加每日一言到邮件内容
        email_content += f'\n每日一言:\n{chinese_quote}'

        # 创建邮件
        message = MIMEMultipart()
        message['From'] = sender_email

        # 遍历收件人列表，发送邮件
        for recipient_email in recipient_emails:
            # 使用正则表达式检查邮箱地址是否合法
            if re.match(r"[^@]+@[^@]+\.[^@]+", recipient_email.strip()):
                message['To'] = recipient_email.strip()  # 移除文本两端的空格和换行符
                message['Subject'] = '每日天气预报'

                # 添加邮件内容
                message.attach(MIMEText(email_content, 'plain'))

                # 连接到QQ邮箱SMTP服务器
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)

                # 发送邮件
                server.sendmail(sender_email, recipient_email, message.as_string())

                # 关闭连接
                server.quit()

                print(f'邮件成功发送到：{recipient_email}')
            else:
                print(f'无效的邮箱地址：{recipient_email}')
    else:
        print(f"每日一言请求失败，错误代码: {quote_response.status_code}, 错误信息: {quote_response.text}")
else:
    print(f"天气数据请求失败，错误代码: {weather_response.status_code}, 错误信息: {weather_response.text}")
