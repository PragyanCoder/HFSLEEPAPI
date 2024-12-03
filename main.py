from fastapi import FastAPI
import requests
import threading
import time
import os

# Initialize FastAPI app
app = FastAPI()

# Environment variables
space_url = "https://PragyanPandey-PragyanSangeet.hf.space"  # Replace with your space URL
api_token = os.getenv("API_TOKEN")  # Read API token from environment variable

# Headers for authorization
headers = {
    "Authorization": f"Bearer {api_token}"
}

# Background task for pinging
def ping_space():
    while True:
        try:
            if not api_token:
                print("API token not found. Please set the API_TOKEN environment variable.")
                break

            response = requests.get(space_url, headers=headers)
            if response.status_code == 200:
                print("Private Space is active!")
            else:
                print(f"Space responded with status code: {response.status_code}")
        except Exception as e:
            print(f"Error pinging the private space: {e}")
        time.sleep(6 * 60 * 60)  # Run every 6 hours

# Start the background thread
thread = threading.Thread(target=ping_space, daemon=True)
thread.start()

@app.get("/dev")
def dev():
    return {"message": "Welcome to the dev endpoint!", "username": "@pragyan"}
