#!/usr/bin/env python3
import os
import sys
import time
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --------------------------
# CONFIGURATION FROM ENV VARS
# --------------------------
URL = os.getenv("PRODUCT_URL")
KEYWORD = os.getenv("PRODUCT_KEYWORD", "Add to cart")  # Default if not set
REQUEST_METHOD = os.getenv("REQUEST_METHOD", "GET").upper()  # Default to GET
REQUEST_PAYLOAD = os.getenv("REQUEST_PAYLOAD")  # JSON string for POST data
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
        # Prepare request parameters
        request_kwargs = {
            "url": URL,
            "timeout": 10
        }

        # Handle POST requests with payload
        if REQUEST_METHOD == "POST":
            if REQUEST_PAYLOAD:
                try:
                    # Try to parse as JSON first
                    payload = json.loads(REQUEST_PAYLOAD)
                    request_kwargs["json"] = payload
                    log(f"Using JSON payload: {REQUEST_PAYLOAD}")
                except json.JSONDecodeError:
                    # If not valid JSON, treat as form data
                    # Parse simple key=value&key2=value2 format
                    payload = {}
                    for pair in REQUEST_PAYLOAD.split('&'):
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            payload[key] = value
                    request_kwargs["data"] = payload
                    log(f"Using form data payload: {payload}")

            response = requests.post(**request_kwargs)
        else:
            # Default to GET request
            response = requests.get(**request_kwargs)

        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        if KEYWORD.lower() in soup.get_text().lower():
            log(f"[ALERT] Product available at {URL}")
            send_pushover(f"The product is now available!\n{URL}")
        else:
            log("Not yet available.")
            # Strip empty lines from the webpage content
            page_text = soup.get_text().lower()
            cleaned_text = '\n'.join(line for line in page_text.splitlines() if line.strip())
            log(cleaned_text)
    except Exception as e:
        log(f"Error checking product: {e}")

# --------------------------
# MAIN EXECUTION
# --------------------------
if __name__ == "__main__":
    check_product()
