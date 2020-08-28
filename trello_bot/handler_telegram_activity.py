from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class TelegramActivityHandler(BaseHTTPRequestHandler):


    start_command_message = "Hi! I'm smart bot and I'll help you to stay tuned for your Trello board. \
    \n\rJust type '/register' and specify user filter to receive notifications from me. I can notife you about: \
    \n\t1) Updating tickets\
    \n\t2) Moving tickets\
    \n\t3) ...all other functions will be created later"

    def do_POST(self):
        print("[INFO] Received POST request on {path}".format(path = self.path))
        if self.path != str("/" + self.server.telegram_token):
            self.send_response(401)
            self.send_header('Content-type','text/html')
            self.end_headers()
            return 

        telegram_payload_info = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        chat_id = str(telegram_payload_info['message']['chat']['id'])
        incoming_msg = str(telegram_payload_info['message']['text'])
        print("[DEBUG] Received the next JSON payload: \n{}".format(json.dumps(telegram_payload_info, indent = 2)))

        isItCommandReceived = False
        for field in telegram_payload_info['message']:
            if field == 'entities' and telegram_payload_info['message']['entities'][0]['type'] == 'bot_command':
                isItCommandReceived = True
                self.process_message(chat_id, incoming_msg)

        if not isItCommandReceived:
            self.process_command(chat_id, incoming_msg)

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        return

    def process_message(self, chat_id, incoming_msg):
        if incoming_msg == '/subscribe' and self.is_current_user_active(chat_id):
            self.server.telegram_api_utils.send_message(chat_id, "Enter usernames for the things you want to follow on the board "
                + "(or write 'ALL' to keep track of everything): ")
            self.upsert_telegram_user_activity_log(chat_id, incoming_msg)
        elif incoming_msg == '/register':
            self.server.telegram_api_utils.send_message(chat_id, "Please, provide your invite token here: ")
            self.upsert_telegram_user_activity_log(chat_id, incoming_msg)
        elif incoming_msg == '/start':
            self.server.telegram_api_utils.send_message(chat_id, TelegramActivityHandler.start_command_message)
            self.reset_last_user_command(chat_id)
        return

    def process_command(self, chat_id, incoming_msg):
        telegram_users_activity_log = self.server.mongodb_utils.findTelegramUserActivityLogByChatId(chat_id)
        # collect data for /register command and substeps
        if telegram_users_activity_log['last_event'] == '/register':
            if incoming_msg == self.server.telegram_bot_invite_token:
                self.server.telegram_api_utils.send_message(
                    chat_id, 
                    "Thank you, you have successfully logged in!\nPlease, enter your trello username:"
                )
                self.upsert_telegram_user_activity_log(chat_id, '/register_step2')
                self.upsert_user_telegram_trello_assignment(chat_id, None, [], True)
            else:
                self.server.telegram_api_utils.send_message(
                    chat_id, 
                    "<b>You shall not pass !!!</b> " + u'\U0001F6B7'
                    "\nSorry, but you entered the wrong invite token. If you repeat often, I will have to ban you " + u'\U0001F609'
                )
                self.upsert_user_telegram_trello_assignment(chat_id, None, [], False)
                self.reset_last_user_command(chat_id)
        elif telegram_users_activity_log['last_event'] == '/register_step2' and self.is_current_user_active(chat_id):
            self.upsert_user_telegram_trello_assignment(chat_id, incoming_msg, [], True)
            self.server.telegram_api_utils.send_message(chat_id, u'\U0001F44D' + " Now, you can use /subscribe !")
            self.reset_last_user_command(chat_id)
        # collect data for /subscribe command
        elif telegram_users_activity_log['last_event'] == '/subscribe' and self.is_current_user_active(chat_id): 
            self.server.telegram_api_utils.send_message(chat_id, "The subscription was successful. "
                + "Now I will automatically notify you about changes in accordance with your settings " + u'\U0001F916')
            # TODO: should be refactored here
            trello_username = self.server.mongodb_utils.findUserTelegramTrelloAssignmentByChatId(chat_id)['trello_username']
            result_subscription = 'ALL' if incoming_msg.lower() == 'all' else incoming_msg
            self.upsert_user_telegram_trello_assignment(chat_id, trello_username, [result_subscription], True)
            self.reset_last_user_command(chat_id)
        return

    def upsert_telegram_user_activity_log(self, chat_id, command): 
        user_event = { 
            "last_event": command,
            "chat_id": chat_id
        }
        self.server.mongodb_utils.upsertTelegramUserActivityLog(user_event)
        return

    def reset_last_user_command(self, chat_id): 
        user_event = { 
            "last_event": 'N/A',
            "chat_id": chat_id
        }
        self.server.mongodb_utils.upsertTelegramUserActivityLog(user_event)
        return

    def is_current_user_active(self, chat_id) -> bool:
        active_result = self.server.mongodb_utils.findUserTelegramTrelloAssignmentByChatId(chat_id)
        if active_result == None: 
            return False
        return bool(active_result['active'])

    def upsert_user_telegram_trello_assignment(self, chat_id, trello_username, subscription, active: bool):
        self.server.mongodb_utils.upsertUserTelegramTrelloAssignment(
            { "trello_username": trello_username, "telegram_chat_id": chat_id, "subscription_list": subscription, "active": active }
        )
        return