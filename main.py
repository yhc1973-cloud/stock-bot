import requests
from bs4 import BeautifulSoup
import os
import json

# --- 설정 구간 ---
TOKEN = "8313563094:AAFiKFIwtpxdL7NhwmjhzQIqFItAxCeWY8U"
CHAT_ID = "868396866"
TARGET_URL = "https://www.cnbc.com/2025/12/15/stock-market-today-live-updates.html"
LAST_ID_FILE = "last_post_id.txt"

def translate_and_summarize(text):
    """구글 번역을 이용해 번역 후, 핵심 문장 위주로 다듬습니다."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q={text}"
        res = requests.get(url)
        full_text = "".join([sentence[0] for sentence in res.json()[0]])
        
        # 가독성을 위해 마침표 기준으로 줄바꿈 추가 및 불필요한 공백 제거
        summarized = full_text.replace(". ", ".\n- ").strip()
        return summarized
    except:
        return text

def send_formatted_telegram(title, body):
    # 번역 및 정리
    ko_title = translate_and_summarize(title).split('\n')[0] # 제목은 한 줄만
    ko_body = translate_and_summarize(body)

    # 읽기 쉬운 포맷 구성
    message = f"📌 **CNBC 실시간 마켓 브리핑**\n"
    message += f"━━━━━━━━━━━━━━━\n\n"
    message += f"🚩 **주제: {ko_title}**\n\n"
    message += f"📝 **핵심 요약:**\n- {ko_body}\n\n"
    message += f"🔗 [CNBC 원문에서 확인]({TARGET_URL})"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID, 
        "text": message, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    })

def run_tracker():
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(TARGET_URL, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    posts = soup.select('.LiveBlog-post')
    if not posts: return

    # 마지막 전송 ID 확인
    last_id = ""
    if os.path.exists(LAST_ID_FILE):
        with open(LAST_ID_FILE, "r") as f:
            last_id = f.read().strip()

    new_posts = []
    for post in posts:
        pid = post.get('id')
        if pid == last_id: break
        
        title = post.select_one('.LiveBlog-postTitle')
        content = post.select_one('.LiveBlog-postContent')
        
        if pid and (title or content):
            new_posts.append({
                'id': pid,
                'title': title.get_text(strip=True) if title else "실시간 속보",
                'body': content.get_text(strip=True) if content else ""
            })

    # 최신순 -> 과거순으로 정렬되어 있으므로 역순으로 발송
    new_posts.reverse()
    for p in new_posts:
        send_formatted_telegram(p['title'], p['body'])
        last_id = p['id']

    # 마지막 ID 업데이트
    with open(LAST_ID_FILE, "w") as f:
        f.write(last_id)

if __name__ == "__main__":
    run_tracker()
