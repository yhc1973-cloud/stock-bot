import yfinance as yf
import requests
from datetime import datetime
import pytz

# 1. 텔레그램 설정 (이미 검증된 정보)
TOKEN = "8313563094:AAFiKFIwtpxdL7NhwmjhzQIqFItAxCeWY8U"
CHAT_ID = "868396866"

def get_detailed_report():
    # 한국 시간 설정
    tz_korea = pytz.timezone('Asia/Seoul')
    now = datetime.now(tz_korea).strftime('%Y-%m-%d %H:%M')
    
    # 2. 데이터 수집 대상
    targets = {
        "S&P 500": "^GSPC", 
        "나스닥": "^IXIC", 
        "다우존스": "^DJI", 
        "엔비디아": "NVDA", 
        "테슬라": "TSLA",
        "애플": "AAPL"
    }
    
    report = f"📅 {now} 미 증시 심층 분석 리포트\n"
    report += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # 지수 및 종목 데이터 추출
    market_trend = "혼조세" # 기본값
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                curr, prev = hist['Close'].iloc[-1], hist['Close'].iloc[-2]
                rate = ((curr - prev) / prev) * 100
                emoji = "🔺" if rate > 0 else "🔻"
                report += f"{emoji} {name}: {curr:.2f} ({rate:+.2f}%)\n"
                
                # S&P 500 기준으로 전체 분위기 파악
                if name == "S&P 500":
                    market_trend = "상승 마감" if rate > 0.5 else "하락 마감" if rate < -0.5 else "보합권 유지"
        except:
            continue

    # 3. 1,000자 규모의 자동화 분석 본문
    report += "\n📝 [에이전트 시황 분석]\n"
    report += f"전일 미 증시는 주요 경제 지표 발표를 앞두고 {market_trend}하며 마감했습니다. "
    report += "연준(Fed)의 통화 정책 방향성에 대한 불확실성이 여전
