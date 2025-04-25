# LINE 天氣機器人

這是一個基於 LINE Messaging API 和 OpenWeather One Call API 3.0 的天氣機器人專案，提供以下功能：

- **即時天氣查詢**：用戶透過 LINE 傳送地區名稱（如「台中市霧峰區」），機器人回覆該地區的當前天氣資訊，包括氣溫、體感溫度、濕度、風速和降雨機率。
- **每日天氣推播**：每天早上 8:00（台灣時間）自動推播台中市霧峰區的天氣資訊給指定 LINE 用戶。
- **API 測試工具**：提供一個簡單腳本，用於測試 OpenWeather API 是否正常運作。

## 專案結構

- `weather.py`：測試 OpenWeather One Call API 3.0 是否正常運作，使用台中市霧峰區的經緯度進行 API 請求。
- `webhook_server.py`：LINE Webhook 伺服器，處理用戶的文字訊息，查詢指定地區的天氣並回覆。
- `send_weather_everday.py`：定時任務腳本，每天早上 8:00 推播台中市霧峰區的天氣資訊。

## 功能詳情

### 1. 即時天氣查詢（webhook_server.py）

- **輸入**：用戶在 LINE 聊天中傳送地區名稱（例如「台北市」或「台中市霧峰區」）。
- **處理**：
  - 使用 Google Maps Geocoding API 將地區名稱轉換為經緯度。
  - 使用 OpenWeather One Call API 3.0 獲取天氣資料（`/data/3.0/onecall`）。
  - 回覆天氣資訊，包括：
    - 地區名稱
    - 天氣描述（例如「晴天」）
    - 氣溫（°C）
    - 體感溫度（°C）
    - 濕度（%）
    - 風速（m/s）
    - 降雨機率（%）
- **技術**：Flask（Webhook 伺服器）、LINE Messaging API、Google Maps Geocoding API、OpenWeather API。

### 2. 每日天氣推播（send_weather_everday.py）

- **定時任務**：每天早上 8:00（台灣時間）執行。
- **地區**：預設為台中市霧峰區（可修改）。
- **處理**：
  - 使用 Google Maps Geocoding API 獲取經緯度。
  - 使用 OpenWeather One Call API 3.0 獲取天氣資料。
  - 透過 LINE Push API 推播天氣資訊給指定用戶。
- **技術**：Python `schedule` 模組、LINE Messaging API、Google Maps Geocoding API、OpenWeather API。

### 3. API 測試（weather.py）

- **用途**：驗證 OpenWeather One Call API 3.0 是否正常運作。
- **測試地區**：台中市霧峰區（經緯度：24.0493, 120.6973）。
- **輸出**：列印 API 回應的 JSON 資料，或顯示錯誤訊息（例如 401 Unauthorized）。

## 環境需求

- Python 3.8 或更高版本
- 必要的 Python 套件（見 `requirements.txt`）
- LINE Messaging API 帳戶（需提供 Channel Access Token 和 Channel Secret）
- OpenWeather One Call API 3.0 訂閱（需提供 API Key）
- Google Maps Geocoding API（需提供 API Key）

## 安裝步驟

1. **複製專案**：

   ```bash
   git clone <your-repository-url>
   cd line-weather-bot
   ```

2. **建立虛擬環境（可選）**：

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **安裝依賴**：

   ```bash
   pip install -r requirements.txt
   ```

   `requirements.txt` 內容：

   ```
   flask==2.3.3
   requests==2.31.0
   python-dotenv==1.0.0
   line-bot-sdk==3.11.0
   schedule==1.2.0
   pytz==2023.3
   ```

4. **配置環境變數**：

   - 在專案根目錄創建 `.env` 檔案，加入以下內容：

     ```env
     LINE_CHANNEL_ACCESS_TOKEN=你的_LINE_Channel_Access_Token
     LINE_CHANNEL_SECRET=你的_LINE_Channel_Secret
     OPENWEATHER_API_KEY=你的_OpenWeather_API_KEY
     GOOGLE_MAPS_API_KEY=你的_Google_Maps_API_KEY
     ```
   - **獲取金鑰**：
     - **LINE**：從 LINE Developers Console 獲取 `Channel Access Token`（Messaging API 標籤）和 `Channel Secret`（Basic settings 標籤）。
     - **OpenWeather**：從 OpenWeather Dashboard 獲取 One Call API 3.0 的 API Key。
     - **Google Maps**：從 Google Cloud Console 啟用 Geocoding API 並獲取 API Key。

## 使用方式

### 1. 測試 OpenWeather API（weather.py）

用於驗證 OpenWeather API 金鑰是否有效。

```bash
python weather.py
```

- **成功**：輸出台中市霧峰區的天氣 JSON 資料。
- **失敗**：顯示錯誤訊息（例如 `請求失敗，狀態碼:401`）。

### 2. 運行即時天氣查詢（webhook_server.py）

1. 啟動 Flask 伺服器：

   ```bash
   python webhook_server.py
   ```

   - 預設運行在 `http://localhost:5000`。

2. 使用 ngrok 暴露本地伺服器：

   ```bash
   ngrok http 5000
   ```

   - 複製 ngrok 提供的公開 URL（例如 `https://xxxx.ngrok-free.app`）。

3. 配置 LINE Webhook：

   - 前往 LINE Developers Console，在 Messaging API 設定中將 Webhook URL 設為 `<ngrok-url>/webhook`。
   - 啟用「Use webhook」選項。

4. 測試：

   - 在 LINE 聊天中傳送地區名稱（例如「台中市霧峰區」），機器人應回覆天氣資訊。

### 3. 運行每日天氣推播（send_weather_everday.py）

1. 確認 `.env` 中的 `LINE_CHANNEL_ACCESS_TOKEN` 和 `OPENWEATHER_API_KEY`。
2. 確認 `line_user_id`（預設為 `U6f61657bec2d34ad0c33c371243470e8`）是否正確。
3. 運行腳本：

   ```bash
   python send_weather_everday.py
   ```
   - 腳本將在每天早上 8:00（台灣時間）推播台中市霧峰區的天氣資訊。
   - 測試時，可臨時修改推播時間（例如 `schedule.every().day.at("14:30", taipei_tz).do(send_weather_update)`）。

## 注意事項

1. **環境變數安全**：

   - 不要將 `.env` 檔案上傳到 GitHub。確保 `.gitignore` 包含：

     ```
     .env
     __pycache__/
     *.pyc
     ```

2. **API 金鑰限制**：

   - **OpenWeather**：確保 One Call API 3.0 訂閱有效，每日免費額度為 1,000 次呼叫。
   - **Google Maps**：確認 Geocoding API 已啟用，且未超出每日請求限制。
   - **LINE**：確保 Channel Access Token 和 Channel Secret 有效。

3. **錯誤排查**：

   - **401 Unauthorized（OpenWeather）**：檢查 `.env` 中的 `OPENWEATHER_API_KEY`，或重新生成金鑰。
   - **400 Bad Request（LINE）**：確認 `LINE_CHANNEL_ACCESS_TOKEN` 和 Webhook 簽名。
   - **Geocoding 失敗**：檢查 `GOOGLE_MAPS_API_KEY` 和地區名稱格式。

4. **時區設定**：

   - `send_weather_everday.py` 使用台灣時區（`Asia/Taipei`）。若部署到其他時區，需調整 `pytz.timezone`。

## 範例輸出

### webhook_server.py

用戶輸入：「台中市霧峰區」 機器人回覆：

```
🏙️ 台中市霧峰區
🌤️ 天氣：晴天
🌡️ 氣溫：25.3°C
🌡️ 體感溫度：26.1°C
💧 濕度：65%
🍃 風速：3.2 m/s
☔ 降雨機率：10%
```

### send_weather_everday.py

每日推播（早上 8:00）：

```
🏙️ 台中市霧峰區
🌤️ 天氣：多雲
🌡️ 氣溫：24.8°C
🌡️ 體感溫度：25.5°C
💧 濕度：70%
🍃 風速：2.8 m/s
☔ 降雨機率：20%
```

## 未來改進

- 支援多用戶推播（動態配置 `line_user_id`）。
- 新增天氣預報（例如未來 3 天）。
- 提供更豐富的回覆格式（例如圖片或 Flex Message）。
- 部署到雲端服務（例如 Heroku 或 AWS），取代本地 ngrok。

## 聯繫

如有問題，請聯繫專案維護者或提交 GitHub Issue。