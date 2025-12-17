import yfinance as yf
import requests
from datetime import datetime
import pytz

# 설정 정보 (제공해주신 데이터)
TELEGRAM_TOKEN = "8313563094:AAFiKFIwtpxdL7NhwmjhzQIqFItAxCeWY8U"
CHAT_ID = "868396866"

def get_market_report():
    tz_korea = pytz.timezone('Asia/Seoul')
    now = datetime.now(tz_korea).strftime('%Y-%m-%d %H:%M')
    targets = {"S&P 500": "^GSPC", "나스닥": "^IXIC", "엔비디아": "NVDA", "테슬라": "TSLA"}
    report = f"📅 {now} 미 증시 요약\n━━━━━━━━━━━━━━━\n"
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            curr, prev = hist['Close'].iloc[-1], hist['Close'].iloc[-2]
            rate = ((curr - prev) / prev) * 100
            emoji = "🔺" if curr > prev else "🔻"
            report += f"{emoji} {name}: {curr:.2f} ({rate:+.2f}%)\n"
        except: continue
    report += "━━━━━━━━━━━━━━━\n✅ 자동화 서버 발송 완료"
    return report

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    send_telegram(get_market_report())
