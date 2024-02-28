import argparse
import copy
import getpass
import json

import mysql.connector as sqllib
from flask import Flask, render_template, request

import apis.page as page

def main(sql_host, sql_user, sql_pass, sql_db):

    app = Flask(__name__)
    msg = page.define(app, sql_host, sql_user, sql_pass, sql_db)

    @app.route("/")
    @app.route("/msg")
    def page_msg():
        return render_template("index.html")

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
