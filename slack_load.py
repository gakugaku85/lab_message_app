from datetime import datetime

import mysql.connector
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import api_keys

def get_bot_api_token():
    return api_keys.SLACK_BOT_USER_TOKEN

def get_slack_api_token():
    return api_keys.SLACK_API_TOKEN

app = App(token=get_bot_api_token())

@app.event({"type": "message"})
def get_message(event, say):
    print(event)
    print(find_username_by_id(event["user"]))
    # add_data_to_database(event["text"], find_username_by_id(event["user"]))

def find_username_by_id(user_id: str) -> str:
    response = requests.get(
        f"https://slack.com/api/users.profile.get?user={user_id}",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {get_bot_api_token()}"},
    )
    return response.json()["profile"]["real_name"]

if __name__ == "__main__":
    handler = SocketModeHandler(app, get_slack_api_token())
    handler.start()
