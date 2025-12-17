import requests
from bs4 import BeautifulSoup
import os

# --- 설정 구간 ---
TOKEN = "8313563094:AAFiKFIwtpxdL7NhwmjhzQIqFItAxCeWY8U"
CHAT_ID = "868396866"
LAST_ID_FILE = "last_post_id.txt"

def get_realtime_target_url():
    """CNBC 메인에서 '오늘의 실시간 업데이트' 기사 주소를 자동으로 찾아옵니다."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # CNBC 시장 뉴스 목록 페이지
        base_url = "https://www.cnbc.com/world-markets/"
        res = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 'stock-market-today-live-updates' 단어가 포함된 최신 링크 검색
        for a in soup.find_all('a', href=True):
            if 'stock-market-today-live-updates' in a['href']:
                url = a['href']
                return url if url.startswith('http') else f"https://www.cnbc.com{url}"
    except:
        pass
    # 못 찾을 경우 대비한 기본 주소
    return "https://www.cnbc.com/world-markets/"

def translate_and_clean(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q={text}"
        res = requests.get(url, timeout=10)
        full_text = "".join([sentence[0] for sentence in res.json()[0]])
        # 출처 언급 삭제
        full_text = full_text.replace("CNBC", "현지 소식통").replace("씨엔비씨", "현지 매체")
        return full_text.replace(". ", ".\n- ").strip()
    except:
        return text

def send_telegram(title, body):
    ko_title = translate_and_clean(title).split('\n')[0]
    ko_body = translate_and_clean(body)

    msg = f"⚡️ **[실시간] 미 증시 긴급 시황 브리핑**\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"📌 **헤드라인: {ko_title}**\n\n"
    msg += f"📝 **상세 분석:**\n- {ko_body}\n\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"✅ 시장 분석 에이전트 업데이트 완료"

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # [핵심] 매번 실행 시마다 새로운 기사 링크를 자동으로 리프레시합니다.
    target_url = get_realtime_target_url()
    
    try:
        res = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 가장 최신 포스트 1개
        post = soup.select_one('.LiveBlog-post')
        
        if post:
            pid = post.get('id')
            last_id = ""
            if os.path.exists(LAST_ID_FILE):
                with open(LAST_ID_FILE, "r") as f:
                    last_id = f.read().strip()
            
            # 새로운 글(ID가 다름)일 때만 발송
            if pid != last_id:
                title_elem = post.select_one('.LiveBlog-postTitle')
                content_elem = post.select_one('.LiveBlog-postContent')
                title = title_elem.get_text(strip=True) if title_elem else "시장 속보"
                content = content_elem.get_text(strip=True) if content_elem else ""
                
                if content:
                    send_telegram(title, content)
                    with open(LAST_ID_FILE, "w") as f:
                        f.write(pid)
    except Exception as e:
        print(f"Error: {e}")
