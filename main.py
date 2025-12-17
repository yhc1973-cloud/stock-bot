import requests
from bs4 import BeautifulSoup
import yfinance as yf
import os
import re
from datetime import datetime
import pytz

# --- 설정 구간 ---
TOKEN = "8313563094:AAFiKFIwtpxdL7NhwmjhzQIqFItAxCeWY8U"
CHAT_ID = "868396866"
LAST_ID_FILE = "last_post_id.txt"

def is_market_open():
    """전일 미국 시장이 열렸었는지 확인 (휴장일 발송 방지)"""
    try:
        spy = yf.Ticker("^GSPC")
        hist = spy.history(period="1d")
        return not (hist.empty or hist['Volume'].iloc[-1] == 0)
    except:
        return False

def get_latest_link():
    """구글 뉴스 검색에서 최신 시황 업데이트 링크 추출"""
    search_url = "https://www.google.com/search?q=cnbc+stock+market+today+live+updates&tbm=nws"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        res = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        for a in soup.select('a'):
            href = a.get('href', '')
            if 'cnbc.com' in href and 'live-updates' in href:
                match = re.search(r'(https?://www\.cnbc\.com/[^&]+)', href)
                if match: return match.group(1)
    except: pass
    return None

def translate_and_refine(text):
    """번역 및 출처 숨기기 문체 가공"""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q={text}"
        res = requests.get(url, timeout=10)
        full_text = "".join([s[0] for s in res.json()[0]])
        # CNBC 및 관련 단어를 중립적인 표현으로 치환하여 출처를 숨김
        for word in ["CNBC", "씨엔비씨", "Live Updates", "실시간 업데이트"]:
            full_text = full_text.replace(word, "현지 시황팀")
        return full_text.replace(". ", ".\n- ").strip()
    except: return text

def send_telegram(title, body):
    ko_title = translate_and_refine(title).split('\n')[0]
    ko_body = translate_and_refine(body)

    msg = f"🗞 **[데일리] 미 증시 핵심 시황 브리핑**\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🚩 **헤드라인: {ko_title}**\n\n"
    msg += f"📝 **상세 분석:**\n- {ko_body}\n\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"✅ 시장 분석 에이전트 업데이트 완료"

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    # 1. 휴장일 체크
    if not is_market_open():
        print("미국 휴장일입니다. 리포트를 생성하지 않습니다.")
        exit()

    # 2. 최신 뉴스 탐색
    target_url = get_latest_link()
    if not target_url: exit()

    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(target_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    post = soup.select_one('.LiveBlog-post')

    if post:
        pid = post.get('id')
        last_id = ""
        if os.path.exists(LAST_ID_FILE):
            with open(LAST_ID_FILE, "r") as f: last_id = f.read().strip()

        # 3. 새로운 내용이 있을 때만 전송
        if pid != last_id:
            title = post.select_one('.LiveBlog-postTitle').get_text(strip=True) if post.select_one('.LiveBlog-postTitle') else "시장 주요 소식"
            content = post.select_one('.LiveBlog-postContent').get_text(strip=True) if post.select_one('.LiveBlog-postContent') else ""
            if content:
                send_telegram(title, content)
                with open(LAST_ID_FILE, "w") as f: f.write(pid)
