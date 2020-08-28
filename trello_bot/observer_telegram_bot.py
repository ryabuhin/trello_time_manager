from threading import Thread
from services.telegram_api_utils import TelegramApiUtils
from handler_telegram_activity import TelegramActivityHandler
from http.server import HTTPServer
import ssl


# This class is responsible for handling all incoming messages from
# Trello webhook and sending it to trello bot
class TelegramBotObserver(Thread):


    def __init__(self, server_listen_interface, telegram_token: str, telegram_bot_invite_token: str, 
        trello_api_utils, mongodb_utils: str, telegram_server_port: int):
        Thread.__init__(self)
        self.telegram_token = telegram_token
        self.telegram_bot_invite_token = telegram_bot_invite_token
        self.mongodb_utils = mongodb_utils
        self.trello_api_utils = trello_api_utils
        self.server_listen_interface = server_listen_interface
        self.telegram_server_port = telegram_server_port

    def run(self):
        httpd = HTTPServer((self.server_listen_interface, self.telegram_server_port), TelegramActivityHandler)
        httpd.socket = ssl.wrap_socket (httpd.socket, server_side=True, certfile='./certs/trello_bot_bundle.pem')
        httpd.telegram_token = self.telegram_token
        httpd.telegram_api_utils = TelegramApiUtils(self.telegram_token)
        httpd.telegram_bot_invite_token = self.telegram_bot_invite_token
        httpd.mongodb_utils = self.mongodb_utils
        httpd.trello_api_utils = self.trello_api_utils
        httpd.serve_forever()