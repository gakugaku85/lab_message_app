import mysql.connector as sqllib
from flask import Flask, jsonify, request, render_template


def define(app, sql_host, sql_user, sql_pass, sql_db):
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
