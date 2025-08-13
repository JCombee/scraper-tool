#!/usr/bin/env python3
import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --------------------------
# CONFIGURATION FROM ENV VARS
# --------------------------
URL = os.getenv("PRODUCT_URL")
KEYWORD = os.getenv("PRODUCT_KEYWORD", "Add to cart")  # Default if not set
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")
LOG_FILE = os.getenv("LOG_FILE", "/tmp/product_monitor.log")

if not URL or not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
    print("Missing required environment variables: PRODUCT_URL, PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN")
    sys.exit(1)

# --------------------------
# LOGGING
# --------------------------
def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {message}\n")
    print(f"{timestamp} {message}")

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
            log(f"Error sending Pushover notification: {response.text}")
    except Exception as e:
        log(f"Notification error: {e}")

# --------------------------
# MAIN CHECK FUNCTION
# --------------------------
def check_product():
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        if KEYWORD.lower() in soup.get_text().lower():
            log(f"[ALERT] Product available at {URL}")
            send_pushover(f"The product is now available!\n{URL}")
        else:
            log("Not yet available.")
    except Exception as e:
        log(f"Error checking product: {e}")

# --------------------------
# MAIN EXECUTION
# --------------------------
if __name__ == "__main__":
    check_product()
