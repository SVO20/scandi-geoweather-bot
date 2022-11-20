""" Telegram Bot object based on 'requests' lib

bot = Bot(TOKEN)                        - initialize instance of Bot
bot.get_new_messages()                  - get all unread messages from Telegram API
bot.gen_pop_queued_jmsg(self)          - generator to get recieved message from queue
bot.send_textmessage(chat_id, text)     - send text
bot.reply_textmessage(chat_id, user_message_id, text)
                                        - send text in reply to message
bot.send_photomessage(chat_id, b_image) - send bytes as photo letting Telegram
                                          guess input format and compress image itself
bot.delete_message(chat_id, message_id) - detele message by message_id

"""
from typing import Iterator
from collections import deque
from batman import *
import requests



class Bot:
    def __init__(self, mytoken, long_poll_timeout=120):
        self._new_run = True

        self.TELAPI_URL = "https://api.telegram.org/bot{}/".format(mytoken)
        self._long_poll_timeout = long_poll_timeout
        self._last_messages: deque[dict] = deque()
        self._offset = 1

        with batman_area("bot init checktoken"):

            # check mytoken
            j_response = requests.get(self.TELAPI_URL + 'getMe').json()
            if j_response.get('ok') and j_response.get("result", {}).get("username"):
                self.username = "@" + j_response["result"]["username"]
            else:
                self.username = None  # This means initialization failed

    @batman("bot getmsg")
    def get_new_messages(self):
        r = requests.get(self.TELAPI_URL + 'getUpdates',
                         params={'timeout': self._long_poll_timeout,
                                 'offset': self._offset})
        #
        # long poll assumes hanging upthere by _long_poll_timeout seconds when idle
        assert r.ok, f"Request failed. Response from TG: {r.status_code}"

        updates: list = r.json().get("result", list())
        if not updates:
            # no updates
            if self._new_run:
                self._new_run = False
            return
        else:
            pass

        # According to Telegram API   _offset = update_id of last entry + 1
        # set new _offset
        self._offset = updates[-1]["update_id"] + 1

        # skip bunch of messages from the first run
        if self._new_run:
            self._new_run = False
            return

        # ! The only place in Bot class where  _last_messages  updated
        #
        self._last_messages.extend([u.get("message") for u in updates])
        bat(f"{len(self._last_messages)} messages in queue")

    def _gen_pop_queued_msg(self) -> Iterator[dict]:
        if not self._last_messages:
            return
        while len(self._last_messages) > 0:
            yield self._last_messages.popleft()
        else:
            return

    @property
    def it_messages_to_process(self) -> Iterator[dict]:
        return self._gen_pop_queued_msg()

    @batman("bot sendmsg")
    def send_textmessage(self, chat_id, text) -> requests.Response:
        assert chat_id
        return requests.post(self.TELAPI_URL + 'sendMessage',
                             params={"chat_id": chat_id,
                                     'parse_mode': 'HTML',
                                     "text": text,
                                     "disable_web_page_preview": True})

    @batman("bot sendpic")
    def send_photomessage(self, chat_id, b_image) -> requests.Response:
        assert all((chat_id, b_image, isinstance(b_image, bytes)))
        return requests.post(self.TELAPI_URL + 'sendPhoto',
                             params={'chat_id': chat_id},
                             files={'photo': b_image})

    @batman("bot replymsg")
    def reply_textmessage(self, chat_id, user_message_id, text) -> requests.Response:
        assert all((chat_id, user_message_id))
        return requests.post(self.TELAPI_URL + 'sendMessage',
                             params={"chat_id": chat_id,
                                     "reply_to_message_id": user_message_id,
                                     "allow_sending_without_reply": True,
                                     'parse_mode': 'HTML',
                                     "text": text,
                                     "disable_web_page_preview": True})

    @batman("bot replypic")
    def reply_photomessage(self, chat_id, user_message_id, b_image) -> requests.Response:
        assert all((chat_id, user_message_id, b_image, isinstance(b_image, bytes)))
        return requests.post(self.TELAPI_URL + 'sendPhoto',
                             params={"chat_id": chat_id,
                                     "reply_to_message_id": user_message_id},
                             files={'photo': b_image})

    @batman("bot delmsg")
    def delete_message(self, chat_id, message_id) -> requests.Response:
        assert all((chat_id, message_id is not None))
        return requests.post(self.TELAPI_URL + 'deleteMessage',
                             params={"chat_id": chat_id,
                                     "message_id": message_id})

    @batman("bot sendlocation")
    def send_location(self, chat_id, lat, lng) -> requests.Response:
        assert chat_id  # to do lat, lng assertion
        return requests.post(self.TELAPI_URL + 'sendLocation',
                             params={'chat_id': chat_id,
                                     'latitude': lat,
                                     'longitude': lng})
