from fastapi import FastAPI
import requests
import threading
import time
import os

# Initialize FastAPI app
app = FastAPI()

# Environment variables
api_token = os.getenv("API_TOKEN")  # Read API token from environment variable

# Headers for authorization (ensure api_token is set)
if api_token is None:
    raise ValueError("API_TOKEN environment variable is not set!")

headers = {
    "Authorization": f"Bearer {api_token}"
}

# Telegram bot details
telegram_token = "7067388804:AAHo1L6H7V7Y20CTsJDzfsCzahzuarlUDSQ"
telegram_chat_id = "5205300039"

# List of Space URLs to monitor with names
spaces = [
    {"name": "GitHub Music", "url": "https://pragyanpandey-githubmusic.hf.space"},
    {"name": "Pragyan Sangeet", "url": "https://pragyanpandey-pragyansangeet.hf.space"},
    {"name": "Ultroid", "url": "https://pragyanpandey-ultroid.hf.space"},  # Added missing comma here
    {"name": "PragyanStory", "url": "https://pragyanpandey-pragyanstory.hf.space"}  # Added missing comma here
]

# Dictionary to store space statuses
space_statuses = {space["url"]: "Unknown" for space in spaces}

# Function to start a space
def start_space(space_url):
    try:
        response = requests.post(f"{space_url}/api/space/start", headers=headers)
        if response.status_code == 200:
            space_statuses[space_url] = "Space Restarting"
            print(f"Space {space_url} is restarting...")
        else:
            space_statuses[space_url] = f"Failed to Restart: Status {response.status_code}"
            print(f"Error restarting {space_url}. Status code: {response.status_code}")
    except Exception as e:
        space_statuses[space_url] = "Error Starting Space"
        print(f"Error starting {space_url}: {e}")

# Background task for pinging and managing spaces
def monitor_spaces():
    while True:
        for space in spaces:
            space_url = space["url"]
            try:
                # Ping the space
                response = requests.get(space_url, headers=headers)
                if response.status_code == 200:
                    space_statuses[space_url] = "Space Running"
                    print(f"Space {space_url} is running.")
                elif response.status_code == 503:
                    space_statuses[space_url] = "Space Sleeping"
                    print(f"Space {space_url} is sleeping. Attempting to restart...")
                    start_space(space_url)
                else:
                    space_statuses[space_url] = f"Error: Status {response.status_code}"
                    print(f"Space {space_url} responded with status code: {response.status_code}")
            except Exception as e:
                space_statuses[space_url] = "Error Accessing Space"
                print(f"Error accessing {space_url}: {e}")

        # Send status update to Telegram every 3 hours
        send_telegram_update()

        time.sleep(10800)  # Check every 3 hours (10800 seconds)

# Function to send space status updates to Telegram
def send_telegram_update():
    status_summary = "\n".join([f"{space['name']} - Status: {space_statuses[space['url']]}" for space in spaces])
    message = f"Space Status Update:\n\n{status_summary}"

    try:
        # Send message to Telegram using bot
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {
            "chat_id": telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"  # Optional: This allows for rich formatting
        }
        response = requests.post(url, data=payload)

        # Check if the message was successfully sent
        if response.status_code == 200:
            print("Status update sent to Telegram.")
        else:
            print(f"Failed to send message. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

# Start the background thread
thread = threading.Thread(target=monitor_spaces, daemon=True)
thread.start()

@app.get("/dev")
def dev():
    # Prepare status summary with line breaks (without escape characters)
    status_summary = "\n".join([f"{space['name']} - Status: {space_statuses[space['url']]}" for space in spaces])
    
    return {
        "message": "Welcome to the dev endpoint!",
        "username": "@pragyan",
        "status_summary": status_summary
    }
