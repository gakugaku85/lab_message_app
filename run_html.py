import argparse
import copy
import getpass
import json

import mysql.connector as sqllib
from flask import Flask, render_template, request

from slack_load import find_username_by_id

import apis.page as page

def main(sql_host, sql_user, sql_pass, sql_db):

    app = Flask(__name__)
    msg = page.define(app, sql_host, sql_user, sql_pass, sql_db)

    @app.route("/")
    @app.route("/msg")
    def page_msg():
        connection = sqllib.connect(
            host=sql_host,
            user=sql_user,
            password=sql_pass,
            database=sql_db,
        )

        channel_name = "lab_general"
        channel_name = request.args.get("channel", "", type=str)

        cursor = connection.cursor()
        cursor.execute(
            f"SELECT user, message, timestamp FROM slack.{channel_name} ORDER BY timestamp DESC LIMIT 10"
        )

        messages = []
        for user, message, timestamp in cursor:
            messages.append({"user": find_username_by_id(user), "message": message, "time": timestamp})
        cursor.close()
        connection.close()
        return render_template("index.html", messages=messages, channel_name=channel_name)

    app.run(host="0.0.0.0", port=8080, debug=False, threaded=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", "-c", type=str, required=True, help="path of config file."
    )
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    main(config["sql_host"], config["sql_user"], config["sql_pass"], config["sql_db"])
