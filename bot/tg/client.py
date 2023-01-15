import requests

from bot.tg import schemas


class TgClient:
    """Класс для подключения и взаимодействия с ботом"""
    def __init__(self, token: str):
        self.token = token

    def get_url(self, method: str) -> str:
        """Метод подключения к боту через url с токеном"""
        return f'https://api.telegram.org/bot{self.token}/{method}'

    def get_updates(self, offset: int = 0, timeout: int = 60) -> schemas.GetUpdatesResponse:
        """Метод для получения обновлений из чата бота"""
        url = self.get_url('getUpdates')
        response = requests.get(url, params={'offset': offset, 'timeout': timeout})
        return schemas.GET_UPDATES_SCHEMA.load(response.json())     # schema из нашего датакласса

    def send_message(self, chat_id: int, text: str) -> schemas.SendMessageResponse:
        """для отправки сообщений в чат бота"""
        url = self.get_url('sendMessage')       # метод для отправки sendMessage
        response = requests.get(url, params={'chat_id': chat_id, 'text': text})
        return schemas.SEND_MESSAGE_RESPONSE_SCHEMA.load(response.json())
