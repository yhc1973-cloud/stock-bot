import requests
from bs4 import BeautifulSoup
import os

# --- 설정 구간 ---
TOKEN = "8313563094:AAFiKFIwtpxdL7NhwmjhzQIqFItAxCeWY8U"
CHAT_ID = "868396866"
LAST_ID_FILE = "last_post_id.txt"

def get_latest_live_url():
    """CNBC에서 매일 바뀌는 최신 라이브 업데이트 기사 주소를 동적으로 찾습니다."""
    try:
        # CNBC 시장 뉴스 목록 페이지
        search_url = "https://www.cnbc.com/world-markets/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 'Stock Market Today'와 'Live Updates'가 포함된 링크 검색
        for a in soup.find_all('a', href=True):
            if 'stock-market-today-live-updates' in a['href']:
                return a['href'] if a['href'].startswith('http') else f"https://www.cnbc.com{a['href']}"
    except:
        pass
    # 찾기 실패 시 기본값 (기존 주소 등)
    return "https://www.cnbc.com/world-markets/"

def translate_and_refine(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q={text}"
        res = requests.get(url, timeout=10)
        full_text = "".join([sentence[0] for sentence in res.json()[0]])
        
        # 출처 언급 제거 및 가공
        full_text = full_text.replace("CNBC", "현지 매체").replace("씨엔비씨", "현지 소식통")
        return full_text.replace(". ", ".\n- ").strip()
    except:
        return text

def send_private_report(title, body):
    ko_title = translate_and_refine(title).split('\n')[0]
    ko_body = translate_and_refine(body)

    msg = f"⚡️ **[실시간] 미 증시 핵심 시황 브리핑**\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"📌 **헤드라인: {ko_title}**\n\n"
    msg += f"📝 **상세 분석:**\n- {ko_body}\n\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"✅ 시장 분석 에이전트 업데이트 완료"

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 1. 오늘 날짜의 새로운 기사 주소를 먼저 찾습니다.
    current_target_url = get_latest_live_url()
    
    try:
        res = requests.get(current_target_url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        post = soup.select_one('.LiveBlog-post')
        
        if post:
            pid = post.get('id')
            last_id = ""
            if os.path.exists(LAST_ID_FILE):
                with open(LAST_ID_FILE, "r") as f: last_id = f.read().strip()
            
            if pid != last_id:
                title_elem = post.select_one('.LiveBlog-postTitle')
                content_elem = post.select_one('.LiveBlog-postContent')
                title = title_elem.get_text(strip=True) if title_elem else "시장 브리핑"
                content = content_elem.get_text(strip=True) if content_elem else ""
                
                if content:
                    send_private_report(title, content)
                    with open(LAST_ID_FILE, "w") as f: f.write(pid)
    except Exception as e:
        print(f"Error: {e}")
