import requests
import json


class TelegramApiUtils:


    TELEGRAM_BOT_TOKEN = ''
    TELEGRAM_API_ENDPOINT = 'https://api.telegram.org'


    def __init__(self, telegram_bot_token):
        self.token = telegram_bot_token
        self.result_api_endpoint = (TelegramApiUtils.TELEGRAM_API_ENDPOINT + "/bot{telegramToken}").format(
            telegramToken = self.token
        )

    def get_me(self):
        method_result_endpoint = self.result_api_endpoint + '/getMe'
        response = requests.get(method_result_endpoint)
        return response.status_code == 200
    
    def get_updates(self) -> []:
        method_result_endpoint = self.result_api_endpoint + '/getUpdates'
        response = requests.get(method_result_endpoint)
        return response.json()
    
    def send_message(self, chat_id: str, msg: str) -> []:
        body = {'chat_id': chat_id, 'text': msg, 'parse_mode': 'HTML'}
        headers = {'Content-Type': 'application/json'}

        method_result_endpoint = self.result_api_endpoint + '/sendMessage'
        response = requests.post(method_result_endpoint, data = json.dumps(body), headers = headers)
        return response.json()