import mysql.connector as sqllib
from flask import Flask, jsonify, request, render_template

if __name__ == "__main__":
    app = Flask(__name__)
    def chart():
        return render_template("index.html")

    app.run(host="0.0.0.0", port=9000, debug=False)