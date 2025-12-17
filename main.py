import requests
from bs4 import BeautifulSoup
import os

# --- 설정 구간 ---
TOKEN = "8313563094:AAFiKFIwtpxdL7NhwmjhzQIqFItAxCeWY8U"
CHAT_ID = "868396866"
# CNBC라는 단어를 직접 사용하지 않기 위해 변수명도 변경
SOURCE_URL = "https://www.cnbc.com/2025/12/15/stock-market-today-live-updates.html"
LAST_ID_FILE = "last_post_id.txt"

def translate_and_refine(text):
    """번역 후 특정 브랜드명 삭제 및 문체 가공"""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q={text}"
        res = requests.get(url, timeout=10)
        full_text = "".join([sentence[0] for sentence in res.json()[0]])
        
        # CNBC 및 관련 단어를 중립적인 표현으로 치환
        full_text = full_text.replace("CNBC", "현지 매체").replace("씨엔비씨", "현지 소식통")
        
        # 가독성을 위한 줄바꿈 정리
        return full_text.replace(". ", ".\n- ").strip()
    except:
        return text

def send_private_report(title, body):
    """출처 언급 없이 깔끔한 브리핑 포맷으로 전송"""
    ko_title = translate_and_refine(title).split('\n')[0]
    ko_body = translate_and_refine(body)

    # 텔레그램 메시지 구성 (CNBC 언급 및 링크 완전 제거)
    msg = f"⚡️ **[실시간] 미 증시 핵심 시황 브리핑**\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"📌 **헤드라인: {ko_title}**\n\n"
    msg += f"📝 **상세 분석:**\n- {ko_body}\n\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"✅ 시장 분석 에이전트 업데이트 완료"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID, 
        "text": msg, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    })

if __name__ == "__main__":
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(SOURCE_URL, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 실시간 업데이트 포스트 추출
        post = soup.select_one('.LiveBlog-post')
        
        if post:
            pid = post.get('id')
            last_id = ""
            
            # 마지막 전송 기록 확인
            if os.path.exists(LAST_ID_FILE):
                with open(LAST_ID_FILE, "r") as f:
                    last_id = f.read().strip()
            
            # 새 글이 올라왔을 때만 실행
            if pid != last_id:
                title_elem = post.select_one('.LiveBlog-postTitle')
                content_elem = post.select_one('.LiveBlog-postContent')
                
                title = title_elem.get_text(strip=True) if title_elem else "시장 주요 소식"
                content = content_elem.get_text(strip=True) if content_elem else ""
                
                if content:
                    send_private_report(title, content)
                    
                    # 상태 업데이트 (ID 저장)
                    with open(LAST_ID_FILE, "w") as f:
                        f.write(pid)
    except Exception as e:
        print(f"오류 발생: {e}")
