FROM python:3.9.0a5-alpine3.11

MAINTAINER andrey.dyachkov@gmail.com

RUN mkdir -p /app/templates
WORKDIR /app
ADD requirements.txt requirements.txt
ADD bot.py bot.py
ADD templates templates/
RUN pip3 install -r requirements.txt

ENTRYPOINT python3 bot.py listen-events