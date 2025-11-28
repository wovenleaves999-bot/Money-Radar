import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import google.generativeai as genai
import feedparser
import time

# --- 1. 读取你刚才填的密钥 ---
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]
RECEIVER_EMAIL = os.environ["RECEIVER_EMAIL"]

# --- 2. 搞钱情报源 (你可以随时回来加链接) ---
rss_sources = {
    "CoinDesk (加密货币)": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Product Hunt (新产品)": "https://www.producthunt.com/feed",
    "36Kr (创投)": "https://36kr.com/feed",
    "Hacker News": "https://hnrss.org/newest?points=100"
}

def get_latest_news():
    print("正在去外网抓取数据...")
    combined_text = ""
    for name, url in rss_sources.items():
        try:
            feed = feedparser.parse(url)
            entries = feed.entries[:4] # 每个源抓前4条
            combined_text += f"\n【来源：{name}】\n"
            for entry in entries:
                combined_text += f"- 标题: {entry.title}\n  链接: {entry.link}\n"
        except Exception as e:
            print(f"{name} 抓取失败: {e}")
    return combined_text

def analyze_with_ai(raw_text):
    print("正在唤醒 Gemini 大脑...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    你是商业情报官。阅读以下新闻：
    {raw_text}
    
    任务：
    1. 过滤掉无聊新闻。
    2. 寻找“套利”、“暴涨”、“新工具”机会。
    3. 用中文写【搞钱日报】，格式：
       💰 **搞钱机会**
       - [项目]：(逻辑)
       - 链接：(URL)
       🚀 **趋势**
       - (内容)
    
    如果没有机会，就说“今日无事”。
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI 分析出错: {e}"

def send_email(content):
    print("正在通过 163 邮箱发送...")
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = Header("暴富雷达", 'utf-8')
    msg['To'] = Header("Boss", 'utf-8')
    msg['Subject'] = Header(f"今日情报 ({time.strftime('%Y-%m-%d')})", 'utf-8')

    try:
        # 163 邮箱服务器
        server = smtplib.SMTP_SSL("smtp.163.com", 465)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, [RECEIVER_EMAIL], msg.as_string())
        server.quit()
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {e}")

if __name__ == "__main__":
    raw_data = get_latest_news()
    if raw_data:
        ai_summary = analyze_with_ai(raw_data)
        send_email(ai_summary)
    else:
        print("没抓到数据")
