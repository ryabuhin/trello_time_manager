#!/bin/bash

ip_address=$1

openssl req -newkey rsa:2048 -sha256 -nodes -keyout trello_bot.key -x509 -days 365 -out trello_bot.pem -subj "/C=UA/ST=Odesa/L=Odesa/O=vriabukhin/CN=${ip_address}"
cp ./trello_bot.key ./trello_bot_bundle.pem
cat ./trello_bot.pem >> ./trello_bot_bundle.pem

printf "\n[INFO] SSL certificates were successfully generated\n"