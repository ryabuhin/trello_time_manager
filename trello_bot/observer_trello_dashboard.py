from threading import Thread
from handler_trello_activity import TrelloActivityHandler
from http.server import HTTPServer


# This class is responsible for handling all incoming messages from
# Trello webhook and sending it to trello bot
class TrelloDashboardObserver(Thread):


    def __init__(self, server_listen_interface, trello_key: str, trello_token: str, telegram_token: str, trello_api_utils, mongodb_utils):
        Thread.__init__(self)
        self.trello_key = trello_key
        self.trello_token = trello_token
        self.telegram_token = telegram_token
        self.mongodb_utils = mongodb_utils
        self.trello_api_utils = trello_api_utils
        self.server_listen_interface = server_listen_interface

    def run(self):
        httpd = HTTPServer((self.server_listen_interface, 8444), TrelloActivityHandler)
        httpd.telegram_token = self.telegram_token
        httpd.mongodb_utils = self.mongodb_utils
        httpd.trello_api_utils = self.trello_api_utils
        httpd.serve_forever()