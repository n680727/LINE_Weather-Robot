import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENWEATHER_API_KEY")

# 台中市霧峰區經緯度
lat = 24.0493
lon = 120.6973

# 使用 One Call API 3.0 的 URL
url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&lang=zh_tw&appid={api_key}"

# 呼叫 API
try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"請求失敗，狀態碼:{response.status_code}，錯誤訊息:{response.text}")
except requests.exceptions.RequestException as e:
    print(f"請求發生錯誤:{e}")
