from datetime import datetime

import mysql.connector
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import traceback
import argparse
import json
import os

import api_keys

def get_bot_api_token():
    return api_keys.SLACK_BOT_USER_TOKEN

def get_slack_api_token():
    return api_keys.SLACK_API_TOKEN

def initialize_database(sql_host, sql_user, sql_password, sql_database):
    os.makedirs("/app/static/images", exist_ok=True)
    connection = mysql.connector.connect(
        host=sql_host,
        user=sql_user,
        password=sql_password,
        database=sql_database,
    )
    cursor = connection.cursor()

    init_commands = ["CREATE DATABASE IF NOT EXISTS slack"]

    channels_create = f"""CREATE TABLE IF NOT EXISTS slack.channels (
    id VARCHAR(255),
    name VARCHAR(255),
    is_archived BOOLEAN,
    updated BIGINT,
    num_members INT
    );"""

    users_create = f"""CREATE TABLE IF NOT EXISTS slack.users (
    id VARCHAR(255),
    real_name VARCHAR(255),
    display_name VARCHAR(255),
    image_url VARCHAR(255)
    );"""

    init_commands.append(channels_create)
    init_commands.append(users_create)

    for command in init_commands:
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
    event_channel_name = find_channel_name_by_id(event["channel"], connection)
    find_username_by_id(event["user"], connection)

    # もしeventにthread_tsがあれば、以下のコマンドでDBに追加する
    if "thread_ts" in event:
        command = f"INSERT INTO slack.{event_channel_name} (user, message, timestamp, type, client_msg_id, team, thread_ts, parent_user_id, blocks, channel, event_ts, channel_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
        command = f"INSERT INTO slack.{event_channel_name}  (user, message, timestamp, type, client_msg_id, team, thread_ts, parent_user_id, blocks, channel, event_ts, channel_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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

def get_username_by_slack_id(user_id):
    response = requests.get(
        f"https://slack.com/api/users.profile.get?user={user_id}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_bot_api_token()}",
        },
    )

    img_url = response.json()["profile"]["image_48"]
    print(img_url)
    urlData = requests.get(img_url).content

    with open(f"/app/static/images/{user_id}.png", "wb") as f:
        f.write(urlData)

    return (
        response.json()["profile"]["real_name"],
        response.json()["profile"]["display_name"],
        img_url,
    )

def find_username_by_id(user_id, connection) -> str:
    cursor = connection.cursor()
    command = f"SELECT real_name, display_name FROM slack.users WHERE id = '{user_id}'"
    cursor.execute(command)
    result = cursor.fetchall()

    if result == [] or "/app/static/images/" + user_id + ".png" not in os.listdir("/app/static/images"):
        real_name, display_name, img_url = get_username_by_slack_id(user_id)
        command = f"INSERT INTO slack.users (id, real_name, display_name, image_url) VALUES ('{user_id}', '{real_name}', '{display_name}', '{img_url}')"
        try:
            cursor.execute(command)
        except Exception:
            traceback.print_exc()
        connection.commit()
    else:
        real_name, display_name = result[0]
        connection.commit()

    cursor.close()

    return display_name if display_name else real_name


def find_channel_info_by_id(channel_id: str) -> str:
    response = requests.get(
        f"https://slack.com/api/conversations.info?channel={channel_id}",
        headers={
            "Content-Type": "application,json",
            "Authorization": f"Bearer {get_bot_api_token()}",
        },
    )
    return response.json()

def get_channel_list():
    channel_list = requests.get(
        f"https://slack.com/api/conversations.list",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_bot_api_token()}",
        },
    )
    return channel_list.json()

def find_channel_name_by_id(channel_id: str, connection) -> str:
    cursor = connection.cursor()
    command = f"SELECT name FROM slack.channels WHERE id = '{channel_id}'"
    cursor.execute(command)
    result = cursor.fetchone()
    if result is None:
        channel_info = find_channel_info_by_id(channel_id)
        commands = []
        commands.append(f"CREATE TABLE IF NOT EXISTS slack.{channel_info['channel']['name']} (user VARCHAR(255), message TEXT, timestamp TIMESTAMP, type VARCHAR(255), client_msg_id VARCHAR(255), team VARCHAR(255), thread_ts VARCHAR(255), parent_user_id VARCHAR(255), blocks TEXT, channel VARCHAR(255), event_ts VARCHAR(255), channel_type VARCHAR(255))")
        commands.append(
            f"INSERT INTO slack.channels (id, name, is_archived, updated, num_members) VALUES ('{channel_id}', '{channel_info['channel']['name']}', {channel_info['channel']['is_archived']}, {channel_info['channel']['updated']}, 0)"
        )
        for command in commands:
            try:
                cursor.execute(command)
            except Exception:
                traceback.print_exc()
        connection.commit()
        return channel_info["channel"]["name"]
    return result[0]


app = App(token=get_bot_api_token())

@app.message()
def get_message(event, say):
    insert_message(event)

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
