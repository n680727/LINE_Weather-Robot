from flask import Flask, request, abort
from dotenv import load_dotenv
import os
import json
import requests

app = Flask(__name__)
load_dotenv()

# 從 .env 中讀取 API 金鑰
line_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
weather_api_key = os.getenv("OPENWEATHER_API_KEY")
google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

line_url = "https://api.line.me/v2/bot/message/reply"
weather_url_base = "https://api.openweathermap.org/data/3.0/onecall"

# 傳送回覆訊息
def send_message(reply_token, message):
    headers = {
        "Authorization": f"Bearer {line_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(line_url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Error sending message: {response.status_code}, {response.text}")

# 使用 Google Maps API 取得經緯度
def get_lat_lon_from_address(address):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": google_api_key
    }
    res = requests.get(geocode_url, params=params)
    if res.status_code == 200:
        results = res.json().get("results")
        if results:
            location = results[0]["geometry"]["location"]
            return location["lat"], location["lng"]
    return None, None

@app.route("/webhook", methods=['POST'])
def webhook():
    body = request.get_data(as_text=True)
    print(f"Request body: {body}")

    try:
        events = json.loads(body).get("events", [])
        for event in events:
            reply_token = event["replyToken"]
            user_message = event["message"]["text"].strip()

            lat, lon = get_lat_lon_from_address(user_message)
            if lat is None or lon is None:
                send_message(reply_token, f"無法找到 {user_message} 的經緯度，請確認地區名稱是否正確。")
                continue

            weather_url = f"{weather_url_base}?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&lang=zh_tw&appid={weather_api_key}"

            try:
                weather_response = requests.get(weather_url)
                if weather_response.status_code == 200:
                    data = weather_response.json()
                    current = data.get("current", {})

                    weather_description = current.get("weather", [{}])[0].get("description", "未知")
                    temperature = current.get("temp", "未知")
                    feels_like = current.get("feels_like", "未知")
                    humidity = current.get("humidity", "未知")
                    wind_speed = current.get("wind_speed", "未知")
                    rain_probability = data.get("daily", [{}])[0].get("pop", 0) * 100  # 降雨機率百分比

                    message = (f"🏙️ {user_message}\n"
                               f"🌤️ 天氣：{weather_description}\n"
                               f"🌡️ 氣溫：{temperature}°C\n"
                               f"🌡️ 體感溫度：{feels_like}°C\n"
                               f"💧 濕度：{humidity}%\n"
                               f"🍃 風速：{wind_speed} m/s\n"
                               f"☔ 降雨機率：{rain_probability:.0f}%")

                    send_message(reply_token, message)
                else:
                    send_message(reply_token, f"無法獲取 {user_message} 的天氣資料。")
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")
                send_message(reply_token, "查詢天氣時發生錯誤，請稍後再試。")

    except Exception as e:
        print(f"Error processing webhook: {e}")
        abort(400)

    return 'OK'

if __name__ == "__main__":
    app.run(debug=True, port=5000)