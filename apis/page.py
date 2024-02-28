import mysql.connector as sqllib
from flask import Flask, jsonify, request, render_template


def define(app, sql_host, sql_user, sql_pass, sql_db):
    # @app.route("/chat", methods=["GET", "POST"])
    # def chat_page():
    #     connection = sqllib.connect(
    #         host=sql_host,
    #         user=sql_user,
    #         password=sql_pass,
    #         database=sql_db,
    #     )

    #     channel_name = request.args.get("channel_name", "", type=str)

    #     cursor = connection.cursor()
    #     cursor.execute(f"SELECT user, message, timestamp FROM slack.{channel_name} ORDER BY timestamp DESC LIMIT 10")

    #     messages = []
    #     for user, message, timestamp in cursor:
    #         messages.append({"user": user, "message": message, "time": timestamp})
    #     cursor.close()
    #     connection.close()

    #     return render_template("index.html", messages=messages, channel_name=channel_name)

    @app.route("/get_channels", methods=["GET"])
    def get_channels():
        connection = sqllib.connect(
            host=sql_host,
            user=sql_user,
            password=sql_pass,
            database=sql_db,
        )

        cursor = connection.cursor()
        cursor.execute("SELECT name FROM slack.channels")

        channels = []
        for name in cursor:
            channels.append(name[0])
        cursor.close()
        connection.close()

        return jsonify(channels)
