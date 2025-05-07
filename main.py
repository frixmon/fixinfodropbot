import time
import requests
import telegram

# === KONFIGURACJA ===
API_KEY = "ta5971daf3cb222b2b1f81ecc73dce7e61"
TELEGRAM_TOKEN = "TU_WSTAW_TOKEN"
CHAT_ID = "TU_WSTAW_CHAT_ID"

MIN_DROP = 0.20  # Spadek minimalny (20%)
SLEEP_SECONDS = 300  # Odstęp czasowy (co 5 minut)

bot = telegram.Bot(token=TELEGRAM_TOKEN)
previous_odds = {}

def fetch_odds():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h,totals,spreads&oddsFormat=decimal"
    response = requests.get(url)
    if response.status_code != 200:
        print("Błąd API:", response.text)
        return []
    return response.json()

def track_drops(events):
    global previous_odds
    for event in events:
        key = event['id']
        for bookmaker in event.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                for outcome in market.get('outcomes', []):
                    label = f"{event['home_team']} vs {event['away_team']} | {market['key']} - {outcome['name']}"
                    current_odd = outcome.get('price')
                    if current_odd is None:
                        continue

                    if key not in previous_odds:
                        previous_odds[key] = {}
                    if label in previous_odds[key]:
                        prev_odd = previous_odds[key][label]
                        if current_odd < prev_odd:
                            drop = (prev_odd - current_odd) / prev_odd
                            if drop >= MIN_DROP:
                                msg = f"📉 Spadek kursu:
{label}
Z {prev_odd:.2f} na {current_odd:.2f} (-{drop*100:.1f}%)"
                                print(msg)
                                try:
                                    bot.send_message(chat_id=CHAT_ID, text=msg)
                                except Exception as e:
                                    print("Błąd Telegrama:", e)
                    previous_odds[key][label] = current_odd

if __name__ == "__main__":
    while True:
        try:
            odds = fetch_odds()
            track_drops(odds)
        except Exception as e:
            print("Błąd główny:", e)
        time.sleep(SLEEP_SECONDS)
