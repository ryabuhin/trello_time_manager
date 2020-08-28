#!/bin/bash

script_path="`dirname \"$0\"`"
CONFIG_DIR_PATH=${CONFIG_DIR_PATH:-${script_path}}

host_machine="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r '.ip_address')"
server_listen_interace="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r '.server_listen_interface')"
trello_key="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .trello_key)"
trello_token="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .trello_token)"
trello_secured_enpoint=$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .trello_secured_enpoint)
telegram_token="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .telegram_token)"
telegram_bot_invite_token="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .telegram_bot_invite_token)"
mongo_path="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .mongo_path)"

trello_dashboard_fullname="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .trello_dashboard_fullname)"
trello_daily_plan_list_name_regexp="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .trello_daily_plan_list_name_regexp)"
trello_weekly_plan_list_name_regexp="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .trello_weekly_plan_list_name_regexp)"
trello_monthly_plan_list_name_regexp="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .trello_monthly_plan_list_name_regexp)"
trello_year_plan_list_name_regexp="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .trello_year_plan_list_name_regexp)"
trello_done_list_name_regexp="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .trello_done_list_name_regexp)"
trello_server_port="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .trello_server_port)"
telegram_server_port="$(cat ${CONFIG_DIR_PATH}/bot_config.json | jq -r .telegram_server_port)"

# generate new SSL certificates
cert_dir="${script_path}/trello_bot/certs"

rm -rf "${cert_dir}/trello_bot.key"
rm -rf "${cert_dir}/trello_bot.pem"
rm -rf "${cert_dir}/trello_bot_bundle.pem"

openssl req -newkey rsa:2048 -sha256 -nodes -keyout "${cert_dir}/trello_bot.key" \
    -x509 -days 365 -out "${cert_dir}/trello_bot.pem" \
    -subj "/C=UA/ST=Odesa/L=Odesa/O=trello_bot/CN=${host_machine}"
cp "${cert_dir}/trello_bot.key" "${cert_dir}/trello_bot_bundle.pem"
cat "${cert_dir}/trello_bot.pem" >> "${cert_dir}/trello_bot_bundle.pem"

printf "\n[INFO/BASH] SSL certificates were successfully generated\n"

# register telegram webhook
curl -F "url=https://${host_machine}:${telegram_server_port}/${telegram_token}" -s \
    -F "certificate=@${cert_dir}/trello_bot_bundle.pem" \
    "https://api.telegram.org/bot${telegram_token}/setWebhook" \
    | jq .

for existingWebhookId in $(curl "https://api.trello.com/1/tokens/${trello_token}/webhooks?key=${trello_key}" -s | jq -r .[].id); do
    result=$(curl -XDELETE "https://api.trello.com/1/tokens/${trello_token}/webhooks/${existingWebhookId}?key=${trello_key}" 2>&1)
    [ ! "$result" == 'The requested resource was not found.' ] \
        && printf "\n[INFO/BASH] Trello webhook with id ${existingWebhookId} was sucessfully deleted\n"
done

# receive dashboard id (and use it as idModel for webhook)
found_board=$(curl "https://api.trello.com/1/members/me/boards?key=${trello_key}&token=${trello_token}" -s \
    | jq ".[] | select (.name == \"${trello_dashboard_fullname}\")" -r)
found_board_id=$(echo "$found_board" | jq -r .id)

# register trello webhook
(sleep 2s && curl -XPOST "https://api.trello.com/1/tokens/${trello_token}/webhooks" -s \
    -H "Content-Type: application/json" \
    -d "{ \"key\": \"${trello_key}\", \"callbackURL\": \"http://${host_machine}:${trello_server_port}/${trello_secured_enpoint}\", 
        \"idModel\":\"${found_board_id}\", \"description\": \"${trello_dashboard_fullname} Dashboard Webhook for host: ${host_machine}\" }" | jq .) &

cd ${script_path}/trello_bot && python3 ./trello_bot_main.py \
 "${server_listen_interace}"\
 "${trello_key}"\
 "${trello_token}"\
 "${telegram_token}"\
 "${telegram_bot_invite_token}"\
 "${mongo_path}"\
 "${trello_secured_enpoint}"\
 "${trello_dashboard_fullname}"\
 "${trello_daily_plan_list_name_regexp}"\
 "${trello_weekly_plan_list_name_regexp}"\
 "${trello_monthly_plan_list_name_regexp}"\
 "${trello_year_plan_list_name_regexp}"\
 "${trello_done_list_name_regexp}"\
 "${trello_server_port}"\
 "${telegram_server_port}"