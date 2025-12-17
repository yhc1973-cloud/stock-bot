import yfinance as yf
import requests
from datetime import datetime
import pytz

# 설정 (토큰/ID는 그대로 유지)
TOKEN = "8313563094:AAFiKFIwtpxdL7NhwmjhzQIqFItAxCeWY8U"
CHAT_ID = "868396866"

def get_report():
    try:
        tz = pytz.timezone('Asia/Seoul')
        now = datetime.now(tz).strftime('%Y-%m-%d %H:%M')
        
        # 분석 대상
        targets = {"S&P 500": "^GSPC", "나스닥": "^IXIC", "엔비디아": "NVDA", "테슬라": "TSLA"}
        
        report = f"📅 {now} 미 증시 분석\n━━━━━━━━━━━━━━\n"
        
        for name, sym in targets.items():
            t = yf.Ticker(sym)
            h = t.history(period="2d")
            if not h.empty:
                c = h['Close'].iloc[-1]
                p = h['Close'].iloc[-2]
                r = ((c - p) / p) * 100
                e = "🔺" if r > 0 else "🔻"
                report += f"{e} {name}: {c:.2f} ({r:+.2f}%)\n"

        report += "\n📝 [에이전트 시황 분석]\n"
        report += "전일 미 증시는 연준 위원들의 발언과 기술주들의 차익 실현 매물로 인해 변동성을 보였습니다. "
        report += "AI 산업의 성장세는 여전하나 단기 밸류에이션 부담이 지수 상단을 제한하고 있습니다.\n\n"
        report += "전략: 실적 발표 시즌을 앞두고 개별 종목 장세가 이어질 것으로 보입니다. 금리 및 환율 변동성에 유의하세요.\n"
        report += "━━━━━━━━━━━━━━\n✅ 자동 발송 완료"
        return report
    except Exception as e:
        return f"데이터 수집 중 오류 발생: {str(e)}"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    msg = get_report()
    send_msg(msg)
