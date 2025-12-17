import requests
from bs4 import BeautifulSoup
import re
import sys

# --- 설정 구간 ---
TOKEN = "8313563094:AAFiKFIwtpxdL7NhwmjhzQIqFItAxCeWY8U"
CHAT_ID = "868396866"

def get_latest_link():
    """구글 검색에서 CNBC 라이브 링크를 더 정밀하게 추출합니다."""
    # 검색어에 'today'를 넣어 최신성을 높입니다.
    search_url = "https://www.google.com/search?q=cnbc+stock+market+today+live+updates&tbm=nws"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 모든 링크를 뒤져서 cnbc 라이브 업데이트 패턴을 찾습니다.
        links = soup.find_all('a', href=True)
        for a in links:
            href = a['href']
            # CNBC 기사이고 live-updates가 포함된 주소인지 확인
            if 'cnbc.com' in href and 'live-updates' in href:
                # 구글 리다이렉트 주소(/url?q=...) 처리
                match = re.search(r'(https?://www\.cnbc\.com/[^&]+)', href)
                if match:
                    return match.group(1)
                elif href.startswith('http'):
                    return href
        
        print("검색 결과에서 적절한 CNBC 링크를 찾지 못했습니다.")
    except Exception as e:
        print(f"구글 검색 중 오류 발생: {e}")
    return None

def translate_and_refine(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q={text}"
        res = requests.get(url, timeout=10)
        full_text = "".join([s[0] for s in res.json()[0]])
        
        # 출처 언급 지우기
        forbidden = ["CNBC", "씨엔비씨", "Live Updates", "실시간 업데이트"]
        for word in forbidden:
            full_text = full_text.replace(word, "현지 시황팀")
        return full_text.replace(". ", ".\n- ").strip()
    except:
        return text

def send_telegram(title, body):
    ko_title = translate_and_refine(title).split('\n')[0]
    ko_body = translate_and_refine(body)

    msg = f"⚡️ **[실시간] 미 증시 긴급 시황 브리핑**\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🚩 **주요 헤드라인: {ko_title}**\n\n"
    msg += f"📝 **상세 분석:**\n- {ko_body}\n\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"✅ 시스템 자동 업데이트 완료"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": CHAT_ID, 
        "text": msg, 
        "parse_mode": "Markdown"
    })
    
    if response.status_code == 200:
        print("텔레그램 전송 성공!")
    else:
        print(f"텔레그램 전송 실패: {response.text}")

if __name__ == "__main__":
    target_url = get_latest_link()
    
    if target_url:
        print(f"최신 뉴스 접속 주소: {target_url}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # CNBC 라이브 블로그의 포스트 구조 확인
        post = soup.select_one('.LiveBlog-post')
        
        if post:
            title_el = post.select_one('.LiveBlog-postTitle')
            content_el = post.select_one('.LiveBlog-postContent')
            
            title = title_el.get_text(strip=True) if title_el else "시장 주요 소식"
            content = content_el.get_text(strip=True) if content_el else ""
            
            if content:
                send_telegram(title, content)
            else:
                print("기사 본문 내용을 추출하지 못했습니다.")
        else:
            print("해당 페이지에서 라이브 포스트 형식을 찾지 못했습니다.")
    else:
        print("대상 URL이 없어 실행을 중단합니다.")
