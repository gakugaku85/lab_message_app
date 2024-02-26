from datetime import datetime

import mysql.connector
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import traceback
import argparse
import json

import api_keys

def get_bot_api_token():
    return api_keys.SLACK_BOT_USER_TOKEN

def get_slack_api_token():
    return api_keys.SLACK_API_TOKEN

def initialize_database(sql_host, sql_user, sql_password, sql_database):
    connection = mysql.connector.connect(
        host=sql_host,
        user=sql_user,
        password=sql_password,
        database=sql_database,
    )

    commands = ["CREATE DATABASE IF NOT EXISTS slack",
               "CREATE TABLE IF NOT EXISTS slack.messages (id INT AUTO_INCREMENT PRIMARY KEY, message TEXT, user TEXT, timestamp DATETIME)"]
    cursor = connection.cursor()
    for command in commands:
        try:
            cursor.execute(command)
        except Exception:
            traceback.print_exc()
    connection.commit()
    cursor.close()
    connection.close()

def insert_message(event):
    connection = mysql.connector.connect(
        host=config["sql_host"],
        user=config["sql_user"],
        password=config["sql_pass"],
        database=config["sql_db"],
    )

    print(event)

    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO slack.messages (message, user, timestamp) VALUES (%s, %s, %s)",
        (event["text"], find_username_by_id(event["user"]), datetime.fromtimestamp(float(event["ts"]))),
    )
    connection.commit()
    cursor.close()
    connection.close()

app = App(token=get_bot_api_token())

@app.event({"type": "message"})
def get_message(event, say):
    insert_message(event)

def find_username_by_id(user_id: str) -> str:
    response = requests.get(
        f"https://slack.com/api/users.profile.get?user={user_id}",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {get_bot_api_token()}"},
    )
    return response.json()["profile"]["real_name"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", "-c", type=str, required=True, help="path of config file."
    )
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    initialize_database(config["sql_host"], config["sql_user"], config["sql_pass"], config["sql_db"])

    handler = SocketModeHandler(app, get_slack_api_token())
    handler.start()
