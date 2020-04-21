import requests
import re
import schedule
import time
from datetime import datetime, timedelta
from threading import Thread
from services.trello_api_utils import TrelloApiUtils


# This class is responsible for cards transfering between lists. 
# For example, every day at 00:00 AM move all cards from 'Daily Plan'
# column to 'Weekly Plan' and the same for 'Weekly' to 'Monthly'
class TrelloDashboardCollectorScheduler(Thread):

    TRELLO_BOARD_NAME='Productivity'

    def __init__(self, trello_key: str, trello_token: str):
        Thread.__init__(self)
        self.trello_key = trello_key
        self.trello_token = trello_token
        schedule.every().day.at('00:00').do(self.moveTickets)

    def moveTickets(self):
        trelloApiUtils = TrelloApiUtils(trello_key = self.trello_key, trello_token = self.trello_token)

        board_id = trelloApiUtils.getSpecificBoardIdByName(TrelloDashboardCollectorScheduler.TRELLO_BOARD_NAME)
        daily_plan_list_info = trelloApiUtils.getSpecificListInfoByNameRegexp(board_id, '^Daily Plan ')
        weekly_plan_list_info = trelloApiUtils.getSpecificListInfoByNameRegexp(board_id, '^Weekly Plan ')

        # move all cards from 'Daily Plan' list into 'Weekly Plan'
        for dailyCard in trelloApiUtils.getAllCardsInfoByListId(daily_plan_list_info['id']):
            trelloApiUtils.transferCardTo(dailyCard['id'], weekly_plan_list_info['id'])
            
        current_day_and_month = "{day}.{month}".format(day = datetime.now().day, month = f"{datetime.now():%m}")
        daily_column_new_title = "Daily Plan ({today})".format(today = current_day_and_month)
        # update title for daily column
        trelloApiUtils.updateListTitleById(daily_plan_list_info['id'], daily_column_new_title)

        weekly_column_date_deadline = re.search(r'\([0-9]{1,2}.[0-9]{1,2} - ([0-9]{1,2}.[0-9]{1,2})\)', weekly_plan_list_info['name']).group(1)
        if weekly_column_date_deadline == current_day_and_month: 
            monthly_plan_list_info = trelloApiUtils.getSpecificListInfoByNameRegexp(board_id, '^Monthly Plan ')
            # move all cards from 'Weekly Plan' list into 'Monthly Plan'
            for weeklyCard in trelloApiUtils.getAllCardsInfoByListId(weekly_plan_list_info['id']):
                trelloApiUtils.transferCardTo(weeklyCard['id'], monthly_plan_list_info['id'])
            
            # update title for weekly column
            weekly_column_new_title = "Weekly Plan ({startDay}.{startMonth} - {endDay}.{endMonth})".format(
                startDay = datetime.now().day, startMonth = f"{datetime.now():%m}",
                endDay = (datetime.now() + timedelta(days = 7)).day, endMonth = f"{(datetime.now() + timedelta(days = 7)):%m}"
            )
            trelloApiUtils.updateListTitleById(weekly_plan_list_info['id'], weekly_column_new_title)

            # update title of monthly column
            monthly_column_new_title = "Monthly Plan ({newDate})".format(newDate = f"{datetime.now():%m.%y}")
            trelloApiUtils.updateListTitleById(monthly_plan_list_info['id'], monthly_column_new_title)
        else:
            print("[INFO] Today isn't the end of the week")

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)