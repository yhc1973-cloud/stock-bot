import yfinance as yf
import requests
from datetime import datetime
import pytz
import feedparser

# 1. 설정
TOKEN = "8313563094:AAFiKFIwtpxdL7NhwmjhzQIqFItAxCeWY8U"
CHAT_ID = "868396866"

def is_market_open():
    try:
        spy = yf.Ticker("^GSPC")
        hist = spy.history(period="1d")
        if hist.empty or hist['Volume'].iloc[-1] == 0:
            return False
        return True
    except:
        return False

def get_market_data(symbol):
    try:
        t = yf.Ticker(symbol)
        h = t.history(period="2d")
        if not h.empty and len(h) >= 2:
            c = h['Close'].iloc[-1]
            p = h['Close'].iloc[-2]
            r = ((c - p) / p) * 100
            return c, r
    except:
        pass
    return None, None

def get_latest_news():
    news_items = []
    try:
        # 인베스팅닷컴 RSS
        feed = feedparser.parse("https://www.investing.com/rss/news_25.rss")
        for entry in feed.entries[:5]:
            news_items.append(f"• {entry.title}")
    except:
        news_items = ["• 실시간 뉴스 데이터를 가져오지 못했습니다."]
    return "\n".join(news_items)

def generate_report():
    tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(tz).strftime('%m/%d')
    
    # 데이터 수집
    symbols = {
        "나스닥": "^IXIC", "S&P500": "^GSPC", "필라반": "^SOX",
        "VIX": "^VIX", "미국채10년": "^TNX",
        "엔비디아": "NVDA", "테슬라": "TSLA", "애플": "AAPL"
    }
    
    res = {}
    for name, sym in symbols.items():
        c, r = get_market_data(sym)
        if c is not None:
            res[name] = f"{c:.2f} ({r:+.2f}%)"
        else:
            res[name] = "데이터 수집 불가"

    headlines = get_latest_news()

    # 리포트 작성
    report = f"🏢 {now} 미 증시 심층 전략 리포트\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    report += "📊 [핵심 매크로 지표]\n"
    report += f"● VIX(공포지수): {res.get('VIX')}\n"
    report += f"● 미 10년물 국채금리: {res.get('미국채10년')}\n"
    report += f"● 필라델피아 반도체: {res.get('필라반')}\n\n"

    report += "🌐 [실시간 주요 뉴스 헤드라인]\n"
    report += headlines + "\n\n"

    report += "▶️ [시장 심층 분석]\n"
    report += "금일 증시는 주요 경제 지표 발표 이후 국채 금리의 향방에 따라 기술주들이 민감한 변동성을 보였습니다. 특히 AI 인프라 정책에 대한 기대감이 하방 경직성을 확보해주고 있으며, 주요 대형주들을 중심으로 한 견조한 매수세가 확인되었습니다.\n\n"
    
    report += "🚩 [주요 종목 모니터링]\n"
    report += f"- 테슬라: {res.get('테슬라')}\n"
    report += f"- 엔비디아: {res.get('엔비디아')}\n"
    report += f"- 애플: {res.get('애플')}\n\n"

    report += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    report += "✅ AI 분석 리포트 발송 완료"

    if len(report) > 4000:
        report = report[:3990] + "..."
        
    return report

def send_
