import requests
import json
import re


class TrelloApiUtils: 


    TRELLO_API_ENDPOINT = 'https://api.trello.com'
    TRELLO_API_ENDPOINT_MEMBERS = "{TRELLO_API_ENDPOINT}/1/members".format(TRELLO_API_ENDPOINT = TRELLO_API_ENDPOINT)
    TRELLO_API_ENDPOINT_BOARDS = "{TRELLO_API_ENDPOINT}/1/boards".format(TRELLO_API_ENDPOINT = TRELLO_API_ENDPOINT)
    TRELLO_API_ENDPOINT_LISTS = "{TRELLO_API_ENDPOINT}/1/lists".format(TRELLO_API_ENDPOINT = TRELLO_API_ENDPOINT)
    TRELLO_API_ENDPOINT_CARDS = "{TRELLO_API_ENDPOINT}/1/cards".format(TRELLO_API_ENDPOINT = TRELLO_API_ENDPOINT)


    def __init__(self, trello_key, trello_token): 
        self._api_key = trello_key
        self._api_token = trello_token

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
            print("[INFO] Card with ID: '{cardId}' has been transfered into 'Weekly Plan' column".format(cardId = ticket_id))
        else: 
            print("[EROR] Something went wrong while transfering card with ID: '{cardId}' into 'Weekly Plan' column".format(cardId = ticket_id))

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