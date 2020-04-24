import requests
import json
import re


class TrelloApiUtils: 


    TRELLO_API_ENDPOINT = 'https://api.trello.com'
    TRELLO_API_ENDPOINT_MEMBERS = "{TRELLO_API_ENDPOINT}/1/members".format(TRELLO_API_ENDPOINT = TRELLO_API_ENDPOINT)
    TRELLO_API_ENDPOINT_BOARDS = "{TRELLO_API_ENDPOINT}/1/boards".format(TRELLO_API_ENDPOINT = TRELLO_API_ENDPOINT)
    TRELLO_API_ENDPOINT_LISTS = "{TRELLO_API_ENDPOINT}/1/lists".format(TRELLO_API_ENDPOINT = TRELLO_API_ENDPOINT)
    TRELLO_API_ENDPOINT_CARDS = "{TRELLO_API_ENDPOINT}/1/cards".format(TRELLO_API_ENDPOINT = TRELLO_API_ENDPOINT)


    def __init__(self, trello_key, trello_token, trello_dashboard_fullname, trello_daily_plan_list_name_regexp,
                trello_weekly_plan_list_name_regexp, trello_monthly_plan_list_name_regexp, trello_year_plan_list_name_regexp): 
        self._api_key = trello_key
        self._api_token = trello_token
        self.trello_dashboard_fullname = trello_dashboard_fullname
        self.trello_daily_plan_list_name_regexp = trello_daily_plan_list_name_regexp
        self.trello_weekly_plan_list_name_regexp = trello_weekly_plan_list_name_regexp
        self.trello_monthly_plan_list_name_regexp = trello_monthly_plan_list_name_regexp
        self.trello_year_plan_list_name_regexp = trello_year_plan_list_name_regexp

    ## TODO: methods below should be moved into the separate service

    # Move ticket into the daily column
    def trasfer_card_to_daily_column(self, ticket_id):
        dailyColumnInfo = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_daily_plan_list_name_regexp
        )
        self.transferCardTo(ticket_id, dailyColumnInfo['id'])

    # Move ticket into the weekly column
    def trasfer_card_to_weekly_column(self, ticket_id):
        weeklyColumnInfo = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_weekly_plan_list_name_regexp
        )
        self.transferCardTo(ticket_id, weeklyColumnInfo['id'])

    # Move ticket into the monthly column
    def trasfer_card_to_monthly_column(self, ticket_id):
        monthlyColumnInfo = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_monthly_plan_list_name_regexp
        )
        self.transferCardTo(ticket_id, monthlyColumnInfo['id'])

    # Move ticket into the year column
    def trasfer_card_to_year_column(self, ticket_id):
        yearColumnInfo = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_year_plan_list_name_regexp
        )
        self.transferCardTo(ticket_id, yearColumnInfo['id'])

    # Move all tickets from daily plan to weekly
    def transfer_all_cards_from_daily_to_weekly_column(self):
        daily_plan_list_info = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_daily_plan_list_name_regexp
        )
        for dailyCard in self.getAllCardsInfoByListId(daily_plan_list_info['id']):
            self.trasfer_card_to_weekly_column(dailyCard['id'])
    
    # Move all tickets from weekly plan to monthly
    def transfer_all_cards_from_weekly_to_monthly_column(self):
        weekly_plan_list_info = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_weekly_plan_list_name_regexp
        )
        for weeklyCard in self.getAllCardsInfoByListId(weekly_plan_list_info['id']):
            self.trasfer_card_to_monthly_column(weeklyCard['id'])

    # Move all tickets from monthly plan to year
    def transfer_all_cards_from_monthly_to_year_column(self):
        year_plan_list_info = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_monthly_plan_list_name_regexp
        )
        for yearCard in self.getAllCardsInfoByListId(year_plan_list_info['id']):
            self.trasfer_card_to_year_column(yearCard['id'])

    # Get date of daily column
    def get_daily_column_date(self): 
        daily_plan_list_info = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_daily_plan_list_name_regexp
        )
        return re.search(self.trello_daily_plan_list_name_regexp, daily_plan_list_info["name"]).group(1)

    # Get start date of weekly column
    def get_weekly_column_start_date(self): 
        weekly_plan_list_info = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_weekly_plan_list_name_regexp
        )
        return re.search(self.trello_weekly_plan_list_name_regexp, weekly_plan_list_info["name"]).group(1)

    # Get end date of weekly column
    def get_weekly_column_end_date(self): 
        weekly_plan_list_info = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_weekly_plan_list_name_regexp
        )
        return re.search(self.trello_weekly_plan_list_name_regexp, weekly_plan_list_info["name"]).group(2)

    # Get date of monthly column
    def get_monthly_column_date(self): 
        monthly_plan_list_info = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_monthly_plan_list_name_regexp
        )
        return re.search(self.trello_monthly_plan_list_name_regexp, monthly_plan_list_info["name"]).group(1)

    # Get date of year column
    def get_year_column_date(self): 
        year_plan_list_info = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_year_plan_list_name_regexp
        )
        return re.search(self.trello_year_plan_list_name_regexp, year_plan_list_info["name"]).group(1)

    # Update date of daily column
    def update_daily_column_date(self, new_daily_date): 
        daily_plan_list_info = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_daily_plan_list_name_regexp
        )
        daily_column_date = self.get_daily_column_date()
        new_daily_column_title = daily_plan_list_info["name"].replace(daily_column_date, new_daily_date)
        if re.match(self.trello_daily_plan_list_name_regexp, new_daily_column_title):
            self.updateListTitleById(daily_plan_list_info['id'], new_daily_column_title)
        return

    # Update dates of weekly column
    def update_weekly_column_dates(self, new_start_date, new_end_date): 
        weekly_plan_list_info = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_weekly_plan_list_name_regexp
        )
        weekly_start_column_date = self.get_weekly_column_start_date()
        weekly_end_column_date = self.get_weekly_column_end_date()

        new_weekly_column_title = weekly_plan_list_info["name"].replace(weekly_start_column_date, new_start_date)
        new_weekly_column_title = new_weekly_column_title.replace(weekly_end_column_date, new_end_date)

        if re.match(self.trello_weekly_plan_list_name_regexp, new_weekly_column_title):
            self.updateListTitleById(weekly_plan_list_info['id'], new_weekly_column_title)
        return
    
    # Update date of monthly column
    def update_monthly_column_date(self, new_monthly_date): 
        monthly_plan_list_info = self.getSpecificListInfoByNameRegexp(
            self.get_application_dashboard_id(), 
            self.trello_monthly_plan_list_name_regexp
        )
        monthly_column_date = self.get_monthly_column_date()
        new_monthly_column_title = monthly_plan_list_info["name"].replace(monthly_column_date, new_monthly_date)
        if re.match(self.trello_monthly_plan_list_name_regexp, new_monthly_column_title):
            self.updateListTitleById(monthly_plan_list_info['id'], new_monthly_column_title)
        return

    # GET application dashboard id
    def get_application_dashboard_id(self): 
        return self.getSpecificBoardIdByName(self.trello_dashboard_fullname)

    # GET boards. This is request that aimed to /members endpoints
    def _getMembers(self, uri_add: str) -> []:
        httpResponse = requests.get(
            url = TrelloApiUtils.TRELLO_API_ENDPOINT_MEMBERS + uri_add,
            params = { 'key': self._api_key, 'token': self._api_token }
        )
        return httpResponse.json()

    # GET member information by given identifier
    def getMemberById(self, member_id):
        resultEndpoint = TrelloApiUtils.TRELLO_API_ENDPOINT_MEMBERS + "/{memberId}"
        httpResponse = requests.get(
            url = resultEndpoint.format(memberId = member_id),
            params = { 'key': self._api_key, 'token': self._api_token }
        )
        return httpResponse.json()
    
    # GET identifier of necessary/predefined board 
    def getSpecificBoardIdByName(self, board_name) -> str:
        boardsJson = self._getMembers('/me/boards')
        boardInfo = {'id': 'UKNOWN', 'name': 'UKNOWN' }
        for board in boardsJson: 
            if board['name'] == board_name:
                boardInfo['id'] = board['id']
                boardInfo['name'] = board['name']

        print("[DEBUG] Found '{boardName}' board id: {boardId}".format(
            boardName = boardInfo['name'],
            boardId = boardInfo['id']
        ))
        return boardInfo['id']

    # GET all columns/lists for specific board
    def _getAllListsByBoardId(self, board_id: str) -> []:
        resultEndpoint = TrelloApiUtils.TRELLO_API_ENDPOINT_BOARDS + "/{boardId}/lists"
        httpResponse = requests.get(
            url = resultEndpoint.format(boardId = board_id),
            params = { 'key': self._api_key, 'token': self._api_token }
        )
        return httpResponse.json()

    # GET info ({ 'id': '...', 'name': '...' }) for necessary column/list by it's name regexp
    def getSpecificListInfoByNameRegexp(self, board_id: str, col_name_regexp: str) -> str:
        columnsJson = self._getAllListsByBoardId(board_id)
        columnInfo = {'id': 'UKNOWN', 'name': 'UKNOWN' }
        for column in columnsJson: 
            if re.match(col_name_regexp, column["name"]):
                columnInfo['id'] = column['id']
                columnInfo['name'] = column['name']

        print("[DEBUG] Found '{columnName}' column id: {columnId}".format(
            columnName = columnInfo['name'],
            columnId = columnInfo['id']
        ))
        return columnInfo
    
    # GET list of cards info ({ 'id': '...', 'name': '...' }) for specific column
    def getAllCardsInfoByListId(self, column_id: str) -> list:
        resultEndpoint = TrelloApiUtils.TRELLO_API_ENDPOINT_LISTS + "/{columnId}/cards"
        httpResponse = requests.get(
            url = resultEndpoint.format(columnId = column_id),
            params = { 'key': self._api_key, 'token': self._api_token }
        )
        resultCardsInfoList = []
        for card in httpResponse.json(): 
            resultCardsInfoList.append({'id': card['id'], 'name': card['name']})

        return resultCardsInfoList

    # GET full card/ticket info by it's identifier
    def getCardById(self, ticket_id):
        resultEndpoint = TrelloApiUtils.TRELLO_API_ENDPOINT_CARDS + "/{cardId}"
        httpResponse = requests.get(
            url = resultEndpoint.format(cardId = ticket_id),
            params = { 'key': self._api_key, 'token': self._api_token }
        )
        return httpResponse.json()

    # PUT(update) ticket/card into the other column/list by it's id
    # Returns True if card was transfered successfully, otherwise False
    def transferCardTo(self, ticket_id: str, column_id: str) -> bool:
        resultEndpoint = TrelloApiUtils.TRELLO_API_ENDPOINT_CARDS + "/{cardId}"
        httpResponse = requests.put(
            url = resultEndpoint.format(cardId = ticket_id),
            params = { 'idList': column_id, 'key': self._api_key, 'token': self._api_token }
        )

        isSuccess = (httpResponse.status_code == 200)

        if isSuccess:
            print("[INFO] Card with ID: '{cardId}' has been transfered into another column".format(cardId = ticket_id))
        else: 
            print("[EROR] Something went wrong while transfering card with ID: '{cardId}' into another column".format(cardId = ticket_id))

        return isSuccess

    # PUT (update) column/list title by it's id. 
    # Returns True if column was updated successfully, otherwise False
    def updateListTitleById(self, column_id: str, new_title: str) -> bool: 
        resultEndpoint = TrelloApiUtils.TRELLO_API_ENDPOINT_LISTS + "/{columnId}"
        httpResponse = requests.put(
            url = resultEndpoint.format(columnId = column_id),
            params = { 'name': new_title, 'key': self._api_key, 'token': self._api_token }
        )
        
        isSuccess = (httpResponse.status_code == 200)

        if isSuccess: 
            print("[INFO] Column with new title: '{newTitle}' has been updated successfully".format(newTitle = new_title))
        else: 
            print("[ERROR] Column with new title: '{newTitle}' hasn't been updated".format(newTitle = new_title))

        return isSuccess