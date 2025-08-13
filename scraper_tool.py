import os
import time
import requests
from bs4 import BeautifulSoup

# --------------------------
# CONFIGURATION FROM ENV VARS
# --------------------------
URL = os.getenv("PRODUCT_URL")
KEYWORD = os.getenv("PRODUCT_KEYWORD", "Add to cart")  # Default if not set
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))  # Default: 5 min
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")

if not URL or not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
    raise ValueError("Missing required environment variables. Please set PRODUCT_URL, PUSHOVER_USER_KEY, and PUSHOVER_API_TOKEN.")

# --------------------------
# NOTIFICATION FUNCTION
# --------------------------
def send_pushover(message):
    try:
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": PUSHOVER_API_TOKEN,
                "user": PUSHOVER_USER_KEY,
                "message": message,
                "title": "Product Available!",
                "url": URL,
                "url_title": "Buy Now"
            }
        )
        if response.status_code != 200:
            print(f"Error sending Pushover notification: {response.text}")
    except Exception as e:
        print(f"Notification error: {e}")

# --------------------------
# MAIN CHECK FUNCTION
# --------------------------
def check_product():
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        if KEYWORD.lower() in soup.get_text().lower():
            print(f"[ALERT] Product available at {URL}")
            send_pushover(f"The product is now available!\n{URL}")
            return True
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Not yet available...")
            return False

    except Exception as e:
        print(f"Error checking product: {e}")
        return False

# --------------------------
# LOOP
# --------------------------
if __name__ == "__main__":
    print("Starting product monitor...")
    while True:
        if check_product():
            break  # Stop if found (remove to keep checking)
        time.sleep(CHECK_INTERVAL)
