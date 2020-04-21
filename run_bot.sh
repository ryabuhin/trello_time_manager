#!/bin/bash

my_path="`dirname \"$0\"`"
CONFIG_DIR_PATH=${CONFIG_DIR_PATH:-${my_path}}

# external ipv4 address
ip_address="$1"
server_listen_interace="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r '.server_listen_interface')"
trello_key="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .trello_key)"
trello_token="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .trello_token)"
telegram_token="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .telegram_token)"
mongo_path="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .mongo_path)"

# generate new SSL certificates
cert_dir="${my_path}/trello_bot/certs"

rm -rf "${cert_dir}/trello_bot.key"
rm -rf "${cert_dir}/trello_bot.pem"
rm -rf "${cert_dir}/trello_bot_bundle.pem"

openssl req -newkey rsa:2048 -sha256 -nodes -keyout "${cert_dir}/trello_bot.key" \
    -x509 -days 365 -out "${cert_dir}/trello_bot.pem" \
    -subj "/C=UA/ST=Odesa/L=Odesa/O=vriabukhin/CN=${ip_address}"
cp "${cert_dir}/trello_bot.key" "${cert_dir}/trello_bot_bundle.pem"
cat "${cert_dir}/trello_bot.pem" >> "${cert_dir}/trello_bot_bundle.pem"

printf "\n[INFO/BASH] SSL certificates were successfully generated\n"

# register telegram webhook
curl -F "url=https://${ip_address}:8443/${telegram_token}" -s \
    -F "certificate=@${cert_dir}/trello_bot_bundle.pem" \
    "https://api.telegram.org/bot${telegram_token}/setWebhook" \
    | jq .

for existingWebhookId in $(curl "https://api.trello.com/1/tokens/${trello_token}/webhooks?key=${trello_key}" -s | jq -r .[].id); do
    result=$(curl -XDELETE "https://api.trello.com/1/tokens/${trello_token}/webhooks/${existingWebhookId}?key=${trello_key}" 2>&1)
    [ ! "$result" == 'The requested resource was not found.' ] \
        && printf "\n[INFO/BASH] Trello webhook with id ${existingWebhookId} was sucessfully deleted\n"
done

# register trello webhook
(sleep 2s && curl -XPOST "https://api.trello.com/1/tokens/${trello_token}/webhooks" -s \
    -H "Content-Type: application/json" \
    -d "{ \"key\": \"${trello_key}\", \"callbackURL\": \"http://${ip_address}:8444/defc7f7c274c075a0dac5837ff3b0eb864c03ce5\", 
        \"idModel\":\"59a717c0234cca54c376ced0\", \"description\": \"Productivity Dashboard Webhook for host: ${ip_address}\" }" | jq .) &

cd ${my_path}/trello_bot && python3 ./trello_bot_main.py "$server_listen_interace" "${trello_key}" "${trello_token}" "${telegram_token}" "${mongo_path}"