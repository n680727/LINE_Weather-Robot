import requests
import json
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv
import os
import pytz

# 載入環境變數
load_dotenv()

# LINE 設定
line_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_url = "https://api.line.me/v2/bot/message/push"

# OpenWeather API Key
openweather_api_key = os.getenv("OPENWEATHER_API_KEY")

# Google Maps Geocoding API Key
google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

# 預設地區
default_location = "台中市霧峰區"

# LINE 用戶 ID
line_user_id = "U6f61657bec2d34ad0c33c371243470e8"

# 檢查環境變數是否正確載入
if not all([line_token, openweather_api_key, google_api_key]):
    print("錯誤：缺少必要的環境變數，請檢查 .env 檔案")
    exit(1)

def get_coordinates(location):
    """使用 Google Maps Geocoding API 將地區名稱轉換為經緯度"""
    try:
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": location,
            "key": google_api_key,
            "language": "zh-TW",
            "region": "tw"
        }
        response = requests.get(geocode_url, params=params)
        if response.status_code == 200:
            geocode_data = response.json()
            if geocode_data["status"] == "OK" and geocode_data["results"]:
                location_data = geocode_data["results"][0]["geometry"]["location"]
                return location_data["lat"], location_data["lng"]
            else:
                print(f"無法找到 {location} 的經緯度：{geocode_data.get('error_message', '無結果')}")
                return None, None
        else:
            print(f"Geocoding API 請求失敗，狀態碼：{response.status_code}, 錯誤：{response.text}")
            return None, None
    except Exception as e:
        print(f"Geocoding API 請求錯誤：{e}")
        return None, None

def send_weather_update():
    try:
        # 獲取經緯度
        lat, lon = get_coordinates(default_location)
        if lat is None or lon is None:
            print(f"無法獲取 {default_location} 的天氣資料，因經緯度無效")
            return

        # 建立 OpenWeather One Call API 請求
        weather_url = f"https://api.openweathermap.org/data/3.0/onecall"
        params = {
            "lat": lat,
            "lon": lon,
            "exclude": "minutely,hourly,alerts",
            "units": "metric",
            "lang": "zh_tw",
            "appid": openweather_api_key
        }
        response = requests.get(weather_url, params=params)
        if response.status_code == 200:
            data = response.json()
            # 取得天氣資料
            weather_description = data["current"]["weather"][0].get("description", "未知")
            temperature = data["current"].get("temp", "未知")
            feels_like = data["current"].get("feels_like", "未知")
            humidity = data["current"].get("humidity", "未知")
            wind_speed = data["current"].get("wind_speed", "未知")
            rain_probability = data["daily"][0].get("pop", 0) * 100

            message = (
                f"🏙️ {default_location}\n"
                f"🌤️ 天氣：{weather_description}\n"
                f"🌡️ 氣溫：{temperature}°C\n"
                f"🌡️ 體感溫度：{feels_like}°C\n"
                f"💧 濕度：{humidity}%\n"
                f"🍃 風速：{wind_speed} m/s\n"
                f"☔ 降雨機率：{rain_probability:.0f}%"
            )

            headers = {
                "Authorization": f"Bearer {line_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "to": line_user_id,
                "messages": [{"type": "text", "text": message}]
            }

            line_response = requests.post(line_url, headers=headers, json=payload)
            if line_response.status_code == 200:
                print(f"成功發送天氣通知: {datetime.now(pytz.timezone('Asia/Taipei'))}")
            else:
                print(f"LINE API 發送失敗，狀態碼: {line_response.status_code}, 錯誤: {line_response.text}")
        else:
            print(f"OpenWeather API 請求失敗，狀態碼: {response.status_code}, 錯誤: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"請求發生錯誤: {e}")
    except Exception as e:
        print(f"處理天氣資料時發生錯誤: {e}")

# 設定每天早上 8:00 發送（台灣時區）
taipei_tz = pytz.timezone("Asia/Taipei")
schedule.every().day.at("08:00", taipei_tz).do(send_weather_update)

# 永久執行，等待下一個任務
while True:
    schedule.run_pending()
    time.sleep(60)
