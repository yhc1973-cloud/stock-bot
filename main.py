import google.generativeai as genai
import requests
import os
import xml.etree.ElementTree as ET

def get_market_news():
    query = "US Stock Market Summary"
    url = f"https://news.google.com/rss/search?q={query}+when:1d&hl=en-US&gl=US&ceid=US:en"
    response = requests.get(url)
    root = ET.fromstring(response.content)
    news_items = [item.find('title').text for item in root.findall('.//item')[:10]]
    return "\n".join(news_items)

def main():
    # 설정값 읽기
    api_key = os.getenv("GEMINI_API_KEY")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    # API 키 확인 (에러 방지용)
    if not api_key:
        print("에러: GEMINI_API_KEY를 찾을 수 없습니다.")
        return

    # 1. 뉴스 데이터 수집
    market_headlines = get_market_news()
    
    # 2. Gemini AI 분석
    genai.configure(api_key=api_key)
    # 모델 이름을 가장 안정적인 'gemini-1.5-flash'로 설정
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"다음 미국 증시 헤드라인을 보고 투자자를 위해 한국어 3줄 요약해줘:\n{market_headlines}"
    
    try:
        response = model.generate_content(prompt)
        report_text = response.text
    except Exception as e:
        report_text = f"AI 분석 중 오류가 발생했습니다: {str(e)}"

    # 3. 텔레그램 전송
    final_report = f"🇺🇸 오늘의 미국 증시 요약\n\n{report_text}"
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": final_report})

if __name__ == "__main__":
    main()
