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

# Global variable to store space status
space_status = "Unknown"

# Background task for pinging
def ping_space():
    global space_status
    while True:
        try:
            if not api_token:
                space_status = "API Token Missing"
                print("API token not found. Please set the API_TOKEN environment variable.")
                break

            response = requests.get(space_url, headers=headers)
            if response.status_code == 200:
                space_status = "Space is Alive"
                print("Private Space is active!")
            elif response.status_code == 503:
                space_status = "Space is Sleeping"
                print("Space is sleeping.")
            else:
                space_status = f"Error: Status {response.status_code}"
                print(f"Space responded with status code: {response.status_code}")
        except Exception as e:
            space_status = "Error Accessing Space"
            print(f"Error pinging the private space: {e}")
        
        time.sleep(6 * 60 * 60)  # Run every 6 hours

# Start the background thread
thread = threading.Thread(target=ping_space, daemon=True)
thread.start()

@app.get("/dev")
def dev():
    return {
        "message": "Welcome to the dev endpoint!",
        "username": "@pragyan",
        "space_status": space_status
    }
