import mysql.connector as sqllib
from flask import Flask, jsonify, request, render_template


def define(app, sql_host, sql_user, sql_pass, sql_db):
    @app.route("/chat", methods=["GET", "POST"])
    def page_chat():
        connection = sqllib.connect(
            host=sql_host,
            user=sql_user,
            password=sql_pass,
            database=sql_db,
        )

        cursor = connection.cursor()
        cursor.execute("SELECT user, message, timestamp FROM slack.messages ORDER BY timestamp DESC LIMIT 10")

        messages = []
        for user, message, timestamp in cursor:
            messages.append({"user": user, "message": message, "time": timestamp})
        cursor.close()
        connection.close()

        return jsonify(messages)