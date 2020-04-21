from pymongo import MongoClient
import datetime


class MongoDBUtils: 


    # mongodb://root:master@127.0.0.1:27017/admin
    def __init__(self, connection_url):
        self.connection_url = connection_url
        self.mongo_client = MongoClient(connection_url)
        self.db = self.mongo_client['trello_bot']
        self.db_telegram_users_activity_log = self.db['telegram_users_activity_log']
        self.db_user_telegram_trello_assignment = self.db['user_telegram_trello_assignment']

    def findTelegramUserActivityLogByChatId(self, chat_id):
        return self.db_telegram_users_activity_log.find_one({"chat_id": chat_id}, sort = [('date', -1)])

    def findUserTelegramTrelloAssignmentByChatId(self, chat_id):
        return self.db_user_telegram_trello_assignment.find_one({"telegram_chat_id": chat_id}, sort = [('date', -1)])

    def findUserTelegramTrelloAssignmentByTrelloUsername(self, username):
        return self.db_user_telegram_trello_assignment.find_one({"trello_username": username}, sort = [('date', -1)])

    def findTrellloSubscribersByTheirSubscription(self, subscription_list: []):
        return self.db_user_telegram_trello_assignment.find({ 'subscription_list': { '$in': subscription_list} })

    # {_id, last_event, chat_id, date}
    def upsertTelegramUserActivityLog(self, user_event):
        user_event["date"] = datetime.datetime.utcnow()
        # self.db_telegram_users_activity_log.insert_one(user_event)
        self.db_telegram_users_activity_log.update_one({ 'chat_id': user_event['chat_id'] }, { '$set': user_event }, upsert=True)

    # {_id, trello_username, telegram_chat_id, active, subscription_list, date}
    def upsertUserTelegramTrelloAssignment(self, user_telegram_trello_assignment):
        user_telegram_trello_assignment["date"] = datetime.datetime.utcnow()
        self.db_user_telegram_trello_assignment.update_one(
            { 'telegram_chat_id': user_telegram_trello_assignment['telegram_chat_id'] }, 
            { '$set': user_telegram_trello_assignment }, 
            upsert=True
        )