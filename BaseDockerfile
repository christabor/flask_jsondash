FROM python:2.7-slim
MAINTAINER Chris Tabor "dxdstudio@gmail.com"

RUN apt-get update -y
RUN apt-get install python-pip python-dev build-essential --assume-yes
RUN pip install --upgrade pip
RUN pip install gunicorn

COPY . /app
WORKDIR /app

RUN pip install -e .
