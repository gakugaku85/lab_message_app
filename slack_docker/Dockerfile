FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    sudo \
    python3-dev \
    python3-pip \
    python3-wheel \
    python3-setuptools \
    nano \
    tzdata \
    && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

RUN sudo apt-get update && sudo apt-get upgrade -y
ENV TZ Asia/Tokyo
RUN pip3 install --no-cache-dir \
                paramiko==2.7.2 Flask==3.0.2 Flask-Migrate==4.0.5 numpy==1.24.4 cryptography==2.8 mysql-connector-python==8.3.0 slack_bolt==1.18.1 slack_sdk==3.27.0 requests==2.26.0