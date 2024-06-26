import requests
import datetime
import time
from dotenv import load_dotenv
import os

load_dotenv('secrets.env')
bot_access_token: str = os.getenv('BOT_ACCESS_TOKEN')
channel_id: str = os.getenv('CHANNEL_ID')

bot_access_token = os.getenv("BOT_ACCESS_TOKEN")
channel_id = os.getenv("CHANNEL_ID")

# Configuration for the metrics API request
date = datetime.datetime.utcnow()
url_metrics = 'https://metrics.drift.trade/api/ds/query?ds_type=prometheus&requestId=Q100'
obj = {
    "queries": [{
        "datasource": {"type": "prometheus", "uid": "prometheus"},
        "editorMode": "code",
        "expr": "spot_borrow_balance{market=\"USDC\",namespace=\"drift-v2-mainnet-beta\"} / spot_deposit_balance{market=\"USDC\",namespace=\"drift-v2-mainnet-beta\"}",
        "legendFormat": "{{ market }} Total Deposit",
        "range": True,
        "refId": "A",
        "exemplar": False,
        "requestId": "6A",
        "utcOffsetSec": -25200,
        "interval": "",
        "datasourceId": 1,
        "intervalMs": 30000,
        "maxDataPoints": 1888
    }],
    "from": "1710935800577",
    "to": str(int(time.mktime(date.timetuple()) * 1000))
}

# Send API request for the metric
response_metrics = requests.post(url_metrics, json=obj)
response_data = response_metrics.json()
current_usage = response_data['results']['A']['frames'][0]['data']['values'][1][-1]
print(current_usage)

# Check if the current usage is outside the acceptable range (0.4 - 0.78)
if current_usage < 0.4 or current_usage > 0.78:
    # Construct the Telegram API URL for sending a message
    url_telegram = f"https://api.telegram.org/bot{bot_access_token}/sendMessage"

    # Customize the message based on the usage
    if current_usage < 0.4:
        message = f"USDC utilization under 0.4. It's currently at {current_usage}."
    else:
        message = f"USDC utilization over 0.78. It's currently at {current_usage}."

    data = {"chat_id": channel_id, "text": message}

    # Send the alert message via Telegram
    response_telegram = requests.post(url_telegram, data=data)
    print(response_telegram.text)
    print(f"Bot Token: {bot_access_token}")
    print(f"Channel ID: {channel_id}")

    # Check if the message was sent successfully
    if response_telegram.status_code == 200:
        print("Alert sent successfully via Telegram.")
    else:
        print("Error sending alert via Telegram.")
