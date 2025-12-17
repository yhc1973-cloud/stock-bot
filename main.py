import requests
from bs4 import BeautifulSoup
import os
import re

# --- 사용자 설정 ---
TOKEN = "8313563094:AAFiKFIwtpxdL7NhwmjhzQIqFItAxCeWY8U"
CHAT_ID = "868396866"
LAST_ID_FILE = "last_post_id.txt"

def get_latest_cnbc_link():
    """구글 뉴스 검색에서 CNBC 실시간 업데이트 링크를 정밀 추출합니다."""
    # 검색어 최적화: 최신 글을 잡기 위해 날짜순 정렬 옵션 포함
    search_url = "https://www.google.com/search?q=cnbc+stock+market+today+live+updates&tbm=nws"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        res = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        for a in soup.select('a'):
            href = a.get('href', '')
            # CNBC 라이브 업데이트 기사 패턴 확인
            if 'cnbc.com' in href and 'live-updates' in href:
                # 구글 리다이렉트 주소(/url?q=...)인 경우 정규식으로 순수 URL만 추출
                match = re.search(r'(https?://www\.cnbc\.com/[^&]+)', href)
                if match:
                    return match.group(1)
                elif href.startswith('http'):
                    return href
    except Exception as e:
        print(f"검색 실패: {e}")
    return None

def translate_and_summarize(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q={text}"
        res = requests.get(url, timeout=10)
        translated = "".join([s[0] for s in res.json()[0]])
        # CNBC 언급 삭제 및 다듬기
        cleaned = translated.replace("CNBC", "현지 시황팀").replace("씨엔비씨", "현지 매체")
        return cleaned.replace(". ", ".\n- ").strip()
    except: return text

def send_telegram(title, body, url):
    ko_title = translate_and_summarize(title).split('\n')[0]
    ko_body = translate_and_summarize(body)

    message = f"⚡️ **[실시간] 미 증시 긴급 리포트**\n"
    message += f"━━━━━━━━━━━━━━━━━━━━\n\n"
    message += f"📎 **주요 뉴스: {ko_title}**\n\n"
    message += f"📑 **현장 요약:**\n- {ko_body}\n\n"
    message += f"━━━━━━━━━━━━━━━━━━━━\n"
    message += f"✅ 시스템 자동 업데이트 완료"

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})

if __name__ == "__main__":
    target_url = get_latest_cnbc_link()
    print(f"접속 시도 URL: {target_url}")
    
    if not target_url:
        print("최신 기사 링크를 찾지 못했습니다.")
        exit()

    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(target_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    post = soup.select_one('.LiveBlog-post')

    if post:
        pid = post.get('id')
        last_id = ""
        if os.path.exists(LAST_ID_FILE):
            with open(LAST_ID_FILE, "r") as f: last_id = f.read().strip()

        if pid != last_id:
            title_el = post.select_one('.LiveBlog-postTitle')
            content_el = post.select_one('.LiveBlog-postContent')
            title = title_el.get_text(strip=True) if title_el else "속보"
            content = content_el.get_text(strip=True) if content_el else ""
            
            if content:
                send_telegram(title, content, target_url)
                with open(LAST_ID_FILE, "w") as f: f.write(pid)
