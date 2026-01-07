import google.generativeai as genai
import requests
import os
import xml.etree.ElementTree as ET

def get_market_news():
    # 미국 증시 요약(Stock Market Summary) 전문 뉴스를 검색합니다.
    # 'US Stock Market Closing' 키워드를 사용하여 장 마감 분석 뉴스를 타겟팅합니다.
    query = "US Stock Market Morning Briefing or Closing Summary"
    url = f"https://news.google.com/rss/search?q={query}+when:1d&hl=en-US&gl=US&ceid=US:en"
    
    response = requests.get(url)
    root = ET.fromstring(response.content)
    
    news_items = []
    for item in root.findall('.//item')[:15]: # 더 정확한 분석을 위해 15개 헤드라인 수집
        news_items.append(item.find('title').text)
    
    return "\n".join(news_items)

def main():
    # 1. 미국 증시 전문 뉴스 수집
    market_headlines = get_market_news()
    
    # 2. Gemini AI 분석 (전문가 모드)
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    너는 베테랑 월스트리트 애널리스트야. 아래의 최신 미국 증시 헤드라인들을 바탕으로 '오늘의 미국 시장'을 정리해줘.
    
    데이터:
    {market_headlines}
    
    다음 내용을 반드시 포함해서 한국어로 작성해:
    1. 시장 전체 분위기: (예: 하락 마감, 혼조세, 랠리 등)
    2. 지수 움직임의 핵심 원인: (금리, 지표 발표, 지정학적 이슈 등 주요 원인 2가지)
    3. 주요 종목 및 섹터 특이사항: (빅테크, 반도체 등 눈에 띄는 종목 언급)
    4. 투자자에게 주는 짧은 시사점: (오늘 장의 의미 한줄 요약)

    최대한 객관적이고 전문적인 톤으로 작성해줘.
    """
    
    response = model.generate_content(prompt)
    
    # 3. 텔레그램 전송
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    # 메시지가 너무 길면 텔레그램에서 잘릴 수 있으므로 깔끔하게 제목 추가
    final_report = f"🇺🇸 [미국 주식시장 분석 보고서]\n\n{response.text}"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": final_report})

if __name__ == "__main__":
    main()
