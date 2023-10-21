from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import pymysql

pymysql.install_as_MySQLdb()


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://user:password@db/mydatabase"
app.config["UPLOAD_FOLDER"] = "./uploads"

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    file_path = db.Column(db.String(500))


@app.route("/send", methods=["POST"])
def send_message():
    content = request.form["content"]
    file = request.files["file"]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    message = Message(content=content, file_path=file_path)
    db.session.add(message)
    db.session.commit()

    return jsonify({"status": "success"}), 201


@app.route("/messages", methods=["GET"])
def get_messages():
    messages = Message.query.all()
    return (
        jsonify(
            [
                {"id": m.id, "content": m.content, "file_path": m.file_path}
                for m in messages
            ]
        ),
        200,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
