FROM python:3.6.9-slim

RUN apt-get update && \
apt-get install -y jq curl && \
pip install --upgrade pip && \
pip install requests && \
pip install schedule && \
pip install pymongo

ENV TZ='Europe/Kiev'
ENV CONFIG_DIR_PATH='/root/trello/configs'

COPY ./trello_bot/ /root/trello/trello_bot/
COPY ./run_bot.sh /root/trello/

ENTRYPOINT bash /root/trello/run_bot.sh