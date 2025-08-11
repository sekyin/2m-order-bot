# 2m-order-bot
## Telegram Order Bot with Google Sheets

## Features
- Reads menu from Google Sheet tab **Menu**
- Saves orders to tab **Orders**
- Runs 24/7 on Render free tier

## Google Sheet Setup
1. Create a Google Sheet called `Orders`.
2. Add two tabs:
   - `Orders`: columns `Name | Item | Quantity`
   - `Menu`: columns `name | code`

## Google Cloud Setup
- Create a Service Account in Google Cloud Console.
- Enable **Google Sheets API** and **Google Drive API**.
- Download JSON key → name it `service_account.json`.

## Deploy to Render
- Push code to GitHub.
- In Render:
  - Add env vars:
    ```
    BOT_TOKEN=your_botfather_token
    ADMIN_CHAT_ID=your_telegram_id
    SHEET_NAME=Orders
    GOOGLE_CREDS_JSON=service_account.json
    ```
  - Add a Secret File `service_account.json` with your key contents.
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `python bot.py`

