import requests
from datetime import datetime
from urllib.parse import urljoin

from lxml import etree, html

from time_table_api import (
    get_time_table,
    get_timetable_by_day
)
import misc


WEEKDAYS = {
    'понедельник' : 1,
    'вторник' : 2,
    'среда' : 3,
    'четверг' : 4,
    'пятница' : 5,
    'суббота' : 6,
    'воскресенье' : 7
}

proxies = {
  'http': 'http://64.137.191.20:3128',
  'https': 'http://64.137.191.20:3128',
}

token = misc.token


class BotHandler:
    """Class handled bot"""

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):

        method = 'getUpdates'
        params = {
            'timeout': timeout,
            'offset': offset
        }
        resp = requests.get(
            urljoin(
                self.api_url,
                method
            ),
            params,
            proxies=proxies
        )
        return resp.json()['result']

    def send_message(self, chat_id, text):
        """Method send message y chat_id."""

        method = 'sendMessage'
        params = {
            'chat_id': chat_id,
            'text': text
        }

        resp = requests.post(
            urljoin(
                self.api_url,
                method
            ),
            params,
            proxies=proxies
        )
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            # take last by end
            last_update = get_result[-1]
        else:
            
            last_update = None

        return last_update


greet_bot = BotHandler(token)

greetings = ('здравствуй', 'привет', 'ку', 'здорово')
now = datetime.now()


def main():
    new_offset = None
    today = now.day
    hour = now.hour

    while True:
        greet_bot.get_updates(new_offset)

        last_update = greet_bot.get_last_update()
        
        if not last_update:
            continue
        
        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        print(last_chat_text)

        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']
        
        if last_chat_text.lower() in WEEKDAYS.keys():
            day_ = last_chat_text.lower()

            curr_weekday_day = datetime.now().weekday() + 1
            
            greet_bot.send_message(
                last_chat_id, get_timetable_by_day(WEEKDAYS[day_])
            )

        if last_chat_text.lower() in greetings and today == now.day and 6 <= hour < 12:
            greet_bot.send_message(
                last_chat_id, 'Доброе утро, {}'.format(last_chat_name))

        elif last_chat_text.lower() in greetings and today == now.day and 12 <= hour < 17:
            greet_bot.send_message(
                last_chat_id, 'Добрый день, {}'.format(last_chat_name))

        elif last_chat_text.lower() in greetings and today == now.day and 17 <= hour < 23:
            greet_bot.send_message(
                last_chat_id, 'Добрый вечер, {}'.format(last_chat_name))

        new_offset = last_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
