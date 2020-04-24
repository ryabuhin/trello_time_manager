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
    PASSED_TRELLO_SECURED_ENDPOINT = sys.argv[6]
    PASSED_TRELLO_DASHBOARD_FULLNAME = sys.argv[7]
    PASSED_TRELLO_DAILY_PLAN_LIST_NAME_REGEXP = sys.argv[8]
    PASSED_TRELLO_WEEKLY_PLAN_LIST_NAME_REGEXP = sys.argv[9]
    PASSED_TRELLO_MONTHLY_PLAN_LIST_NAME_REGEXP = sys.argv[10]
    PASSED_TRELLO_YEAR_PLAN_LIST_NAME_REGEXP = sys.argv[11]

    mongodb_utils = MongoDBUtils(PASSED_MONGO_PATH)
    trello_api_utils = TrelloApiUtils(
        PASSED_TRELLO_KEY, 
        PASSED_TRELLO_TOKEN, 
        PASSED_TRELLO_DASHBOARD_FULLNAME,
        PASSED_TRELLO_DAILY_PLAN_LIST_NAME_REGEXP,
        PASSED_TRELLO_WEEKLY_PLAN_LIST_NAME_REGEXP,
        PASSED_TRELLO_MONTHLY_PLAN_LIST_NAME_REGEXP,
        PASSED_TRELLO_YEAR_PLAN_LIST_NAME_REGEXP
    )

    # run a trello dashboard collector by scheduling
    tdas = TrelloDashboardCollectorScheduler(trello_api_utils)
    tdas.start()

    # run a trello dashboard activity observer
    tdo = TrelloDashboardObserver(
        SERVER_LISTEN_INTERFACE,
        PASSED_TRELLO_KEY, 
        PASSED_TRELLO_TOKEN, 
        PASSED_TRELLO_SECURED_ENDPOINT,
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