import requests
import sys
import re
from scheduler_trello_dashboard_collector import TrelloDashboardCollectorScheduler
from observer_trello_dashboard import TrelloDashboardObserver
from observer_telegram_bot import TelegramBotObserver
from services.mongodb_utils import MongoDBUtils
from services.trello_api_utils import TrelloApiUtils

def main():
    SERVER_LISTEN_INTERFACE = sys.argv[1]
    PASSED_TRELLO_KEY = sys.argv[2]
    PASSED_TRELLO_TOKEN = sys.argv[3]
    PASSED_TELEGRAM_TOKEN = sys.argv[4]
    PASSED_MONGO_PATH = sys.argv[5]

    mongodb_utils = MongoDBUtils(PASSED_MONGO_PATH)
    trello_api_utils = TrelloApiUtils(trello_key = PASSED_TRELLO_KEY, trello_token = PASSED_TRELLO_TOKEN)

    # run a trello dashboard collector by scheduling
    tdas = TrelloDashboardCollectorScheduler(PASSED_TRELLO_KEY, PASSED_TRELLO_TOKEN)
    tdas.start()

    # run a trello dashboard activity observer
    tdo = TrelloDashboardObserver(
        SERVER_LISTEN_INTERFACE,
        PASSED_TRELLO_KEY, 
        PASSED_TRELLO_TOKEN, 
        PASSED_TELEGRAM_TOKEN, 
        trello_api_utils, 
        mongodb_utils
    )
    tdo.start()

    # run a telegram observer
    teledo = TelegramBotObserver(
        SERVER_LISTEN_INTERFACE,
        PASSED_TELEGRAM_TOKEN, 
        trello_api_utils,
        mongodb_utils
    )
    teledo.start()
    

if __name__ == "__main__":
    main()