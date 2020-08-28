from threading import Thread
from handler_trello_activity import TrelloActivityHandler
from http.server import HTTPServer


# This class is responsible for handling all incoming messages from
# Trello webhook and sending it to trello bot
class TrelloDashboardObserver(Thread):


    def __init__(self, server_listen_interface, trello_key: str, trello_token: str, trello_secured_endpoint: str, 
                telegram_token: str, trello_api_utils, mongodb_utils, trello_server_port: int):
        Thread.__init__(self)
        self.trello_key = trello_key
        self.trello_token = trello_token
        self.telegram_token = telegram_token
        self.trello_secured_endpoint = trello_secured_endpoint
        self.mongodb_utils = mongodb_utils
        self.trello_api_utils = trello_api_utils
        self.server_listen_interface = server_listen_interface
        self.trello_server_port = trello_server_port

    def run(self):
        httpd = HTTPServer((self.server_listen_interface, self.trello_server_port), TrelloActivityHandler)
        httpd.telegram_token = self.telegram_token
        httpd.mongodb_utils = self.mongodb_utils
        httpd.trello_api_utils = self.trello_api_utils
        httpd.trello_secured_endpoint = self.trello_secured_endpoint
        httpd.serve_forever()