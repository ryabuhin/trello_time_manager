import schedule
import time
from datetime import datetime, timedelta
from threading import Thread
from services.trello_api_utils import TrelloApiUtils


# This class is responsible for cards transfering between lists. 
# For example, every day at 00:00 AM move all cards from 'Daily Plan'
# column to 'Weekly Plan' and the same for 'Weekly' to 'Monthly'
class TrelloDashboardCollectorScheduler(Thread):
    

    def __init__(self, trello_api_utils):
        Thread.__init__(self)
        self.trello_api_utils = trello_api_utils
        schedule.every().day.at('00:00').do(self.moveTickets)
        # move all tickets with assigned dates into corresponding columns 
        schedule.every().day.at("00:00").do(self.trello_api_utils.transfer_tickets_to_corresponding_columns_by_its_due_dates)
        schedule.every().day.at("12:00").do(self.trello_api_utils.transfer_tickets_to_corresponding_columns_by_its_due_dates)

    def moveTickets(self):
        # move all cards from 'Daily Plan' list into 'Weekly Plan'
        self.trello_api_utils.transfer_all_cards_from_daily_to_weekly_column()

        current_day_and_month = "{day}.{month}".format(day = datetime.now().day, month = f"{datetime.now():%m}")
        # update title for daily column
        self.trello_api_utils.update_daily_column_date(current_day_and_month)

        weekly_column_date_deadline = self.trello_api_utils.get_weekly_column_end_date()
        if weekly_column_date_deadline == current_day_and_month: 
            # move all cards from 'Weekly Plan' list into 'Monthly Plan'
            self.trello_api_utils.transfer_all_cards_from_weekly_to_monthly_column()
            
            # update title for weekly column
            new_weekly_column_start_date = "{startDay}.{startMonth}".format(
                startDay = datetime.now().day, 
                startMonth = f"{datetime.now():%m}"
            )
            new_weekly_column_end_date = "{endDay}.{endMonth}".format(
                endDay = (datetime.now() + timedelta(days = 7)).day, 
                endMonth = f"{(datetime.now() + timedelta(days = 7)):%m}"
            )
            self.trello_api_utils.update_weekly_column_dates(new_weekly_column_start_date, new_weekly_column_end_date)

            # update title of monthly column
            self.trello_api_utils.update_monthly_column_date("{newDate}".format(newDate = f"{datetime.now():%m.%y}"))
        else:
            print("[INFO] Today isn't the end of the week")

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)