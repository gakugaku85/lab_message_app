FROM python:3.8

WORKDIR /app
COPY . /app

RUN pip install flask flask_sqlalchemy flask_migrate
RUN pip install mysqlclient
RUN pip install pymysql


CMD ["python", "app.py"]
