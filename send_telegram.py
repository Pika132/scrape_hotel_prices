import requests
import os

# Telegram Bot Token and Chat ID
bot_token = '7751308203:AAF_5lHsCIfb5Uo2ZM6FVHcnyofJKm1jwdA'
chat_id = '-4647316485'

# File path (Excel file generated by scraping script)
file_path = 'daily_price_multiple_hotels.xlsx'

# Telegram API URL to send messages
url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

def send_telegram_file(file_path):
    try:
        # Open the file in binary mode
        with open(file_path, 'rb') as file:
            # Send the file via the bot
            response = requests.post(url, data={'chat_id': chat_id}, files={'document': file})
        
        # Check if the message was sent successfully
        if response.status_code == 200:
            print("File sent successfully to Telegram!")
        else:
            print(f"Failed to send file. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error sending file to Telegram: {e}")

if __name__ == "__main__":
    # Ensure the file exists
    if os.path.exists(file_path):
        send_telegram_file(file_path)
    else:
        print(f"File {file_path} not found!")
