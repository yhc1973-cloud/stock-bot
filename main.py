import requests
from bs4 import BeautifulSoup
import os
import re

# --- 설정 구간 ---
TOKEN = "8313563094:AAFiKFIwtpxdL7NhwmjhzQIqFItAxCeWY8U"
CHAT_ID = "868396866"

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
                # 구글 리다이렉트 주소에서 순수 URL 추출
                match = re.search(r'(https?://www\.cnbc\.com/[^&]+)', href)
                if match: return match.group(1)
    except: pass
    return None

def translate_and_refine(text):
    """번역 및 출처 숨기기 가공"""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q={text}"
        res = requests.get(url, timeout=10)
        full_text = "".join([s[0] for s in res.json()[0]])
        # CNBC 및 관련 단어를 중립적인 표현으로 치환
        forbidden = ["CNBC", "씨엔비씨", "Live Updates", "실시간 업데이트"]
        for word in forbidden:
            full_text = full_text.replace(word, "현지 시황팀")
        return full_text.replace(". ", ".\n- ").strip()
    except: return text

def send_telegram(title, body):
    ko_title = translate_and_refine(title).split('\n')[0]
    ko_body = translate_and_refine(body)

    msg = f"⚡️ **[실시간] 미 증시 긴급 시황 브리핑**\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🚩 **주요 헤드라인: {ko_title}**\n\n"
    msg += f"📝 **상세 분석:**\n- {ko_body}\n\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"✅ 시스템 자동 업데이트 완료"

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    # 최신 뉴스 탐색
    target_url = get_latest_link()
    if not target_url:
        print("최신 기사 링크를 찾지 못했습니다.")
        exit()

    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(target_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 페이지 내 가장 최상단 포스트 추출
    post = soup.select_one('.LiveBlog-post')

    if post:
        title_el = post.select_one('.LiveBlog-postTitle')
        content_el = post.select_one('.LiveBlog-postContent')
        
        title = title_el.get_text(strip=True) if title_el else "시장 주요 소식"
        content = content_el.get_text(strip=True) if content_el else ""
        
        if content:
            send_telegram(title, content)
            print("텔레그램 발송 완료")
