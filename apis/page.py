import mysql.connector as sqllib
from flask import Flask, jsonify, request, render_template


def define(app, sql_host, sql_user, sql_pass, sql_db):
    @app.route("/page", methods=["GET"])
    def page_log():
        connection = sqllib.connect(
            host=sql_host,
            user=sql_user,
            password=sql_pass,
            database=sql_db,
        )

        cursor = connection.cursor()
        cursor.execute("SELECT user, message FROM messages")
        messages = []
        for user, message in cursor:
            messages.append({"user": user, "message": message})
        cursor.close()
        connection.close()

        return jsonify(messages)

if __name__ == "__main__":
    app = Flask(__name__)
    define(app)

    app.run(host="0.0.0.0", port=9000, debug=False)