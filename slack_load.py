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

def initialize_database(sql_host, sql_user, sql_password, sql_database, channel_list):
    connection = mysql.connector.connect(
        host=sql_host,
        user=sql_user,
        password=sql_password,
        database=sql_database,
    )

    commands = ["CREATE DATABASE IF NOT EXISTS slack"]

    for channel in channel_list["channels"]:
        if channel["is_archived"] == False:
            commands.append(f"CREATE TABLE IF NOT EXISTS slack.{channel['name']} (user VARCHAR(255), message TEXT, timestamp TIMESTAMP, type VARCHAR(255), client_msg_id VARCHAR(255), team VARCHAR(255), thread_ts VARCHAR(255), parent_user_id VARCHAR(255), blocks TEXT, channel VARCHAR(255), event_ts VARCHAR(255), channel_type VARCHAR(255))")

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

    #もしeventにthread_tsがあれば、以下のコマンドでDBに追加する
    if "thread_ts" in event:
        command = "INSERT INTO slack.lab_general (user, message, timestamp, type, client_msg_id, team, thread_ts, parent_user_id, blocks, channel, event_ts, channel_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        args = (event["user"], event["text"],
                datetime.fromtimestamp(float(event["ts"])),
                event["type"], event["client_msg_id"],
                event["team"], event["thread_ts"],
                event["parent_user_id"],
                json.dumps(event["blocks"]),
                event["channel"],
                event["event_ts"],
                event["channel_type"])

    else:
        command = "INSERT INTO slack.lab_general (user, message, timestamp, type, client_msg_id, team, thread_ts, parent_user_id, blocks, channel, event_ts, channel_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        args = (event["user"], event["text"],
                datetime.fromtimestamp(float(event["ts"])),
                event["type"], event["client_msg_id"],
                event["team"], None,
                None,
                json.dumps(event["blocks"]),
                event["channel"],
                event["event_ts"],
                event["channel_type"])

    cursor = connection.cursor()
    try:
        cursor.execute(command, args)
    except Exception:
        traceback.print_exc()
    connection.commit()
    cursor.close()
    connection.close()

app = App(token=get_bot_api_token())

@app.message()
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

    channel_list = requests.get(
        f"https://slack.com/api/conversations.list",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_bot_api_token()}",
        },
    )

    initialize_database(config["sql_host"], config["sql_user"], config["sql_pass"], config["sql_db"], channel_list.json())
    handler = SocketModeHandler(app, get_slack_api_token())
    handler.start()
