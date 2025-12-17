import requests
from bs4 import BeautifulSoup
import os
import time

# --- 사용자 설정 ---
TOKEN = "8313563094:AAFiKFIwtpxdL7NhwmjhzQIqFItAxCeWY8U"
CHAT_ID = "868396866"
LAST_ID_FILE = "last_post_id.txt"

def get_latest_cnbc_link():
    """구글 검색을 통해 CNBC Live Updates 최신 링크를 추출합니다."""
    search_url = "https://www.google.com/search?q=cnbc+stock+market+today+live+updates&tbm=nws"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 구글 뉴스 섹션의 첫 번째 링크 추출
        # 구글의 선택자 구조는 자주 바뀌므로 a태그 내 cnbc가 포함된 첫 링크를 찾습니다.
        for a in soup.select('a'):
            href = a.get('href', '')
            if 'cnbc.com/202' in href and 'stock-market-today-live-updates' in href:
                if href.startswith('/url?q='):
                    return href.split('/url?q=')[1].split('&')[0]
                return href
    except Exception as e:
        print(f"검색 실패: {e}")
    return None

def translate_and_summarize(text):
    """구글 번역 API를 이용하여 번역 및 가독성 개선"""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q={text}"
        res = requests.get(url, timeout=10)
        translated = "".join([s[0] for s in res.json()[0]])
        
        # 출처 언급 제거 및 불렛포인트 정리
        cleaned = translated.replace("CNBC", "현지 시황팀").replace("씨엔비씨", "현지 매체")
        return cleaned.replace(". ", ".\n- ").strip()
    except:
        return text

def send_telegram(title, body):
    ko_title = translate_and_summarize(title).split('\n')[0]
    ko_body = translate_and_summarize(body)

    message = f"⚡️ **[실시간] 미 증시 긴급 리포트**\n"
    message += f"━━━━━━━━━━━━━━━━━━━━\n\n"
    message += f"📎 **핵심 주제: {ko_title}**\n\n"
    message += f"📑 **현장 요약:**\n- {ko_body}\n\n"
    message += f"━━━━━━━━━━━━━━━━━━━━\n"
    message += f"✅ 시스템 자동 업데이트 완료"

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})

if __name__ == "__main__":
    # 1. 구글 뉴스에서 최신 CNBC 링크 가져오기
    target_url = get_latest_cnbc_link()
    if not target_url:
        print("최신 링크를 찾지 못했습니다.")
        exit()

    # 2. 해당 페이지 접속 및 최신 포스트 추출
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(target_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    post = soup.select_one('.LiveBlog-post')

    if post:
        pid = post.get('id')
        last_id = ""
        if os.path.exists(LAST_ID_FILE):
            with open(LAST_ID_FILE, "r") as f:
                last_id = f.read().strip()

        # 3. 새로운 글일 때만 전송
        if pid != last_id:
            title_el = post.select_one('.LiveBlog-postTitle')
            content_el = post.select_one('.LiveBlog-postContent')
            
            title = title_el.get_text(strip=True) if title_el else "시장 속보"
            content = content_el.get_text(strip=True) if content_el else ""
            
            if content:
                send_telegram(title, content)
                with open(LAST_ID_FILE, "w") as f:
                    f.write(pid)
