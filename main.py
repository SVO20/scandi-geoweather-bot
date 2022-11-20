from batman import *
from collections import defaultdict, deque
from delorean import Delorean
from datetime import timedelta
import shelve

import botobject
import parseryrno

import dotenv
from os import getenv
dotenv.load_dotenv()

token = getenv("TELEGRAM_BOT_TOKEN")
b = botobject.Bot(token)
if b.username:
    bat(f"Started successfully. \nUsername: {b.username}")
else:
    print("Bot not started! \nRun setup.py")
    exit(-1)


# === main cycle ===
while True:
    # fetch new messages
    b.get_new_messages()

    # process each message, queued in bot
    for msg in b.it_messages_to_process:

        # current message
        with batman_area("main cycle processing"):
            # variables check and set up
            if not msg: raise ExitBatmanArea
            if not(message_id := msg.get("message_id")): raise Exception("message_id missed")
            if not(chat_id := msg.get("chat", {}).get("id")): raise Exception("chat_id missed")
            if not(user_id := msg.get("from", {}).get("id")): raise Exception("user_id missed")
            text: str = msg.get("text", "")
            with shelve.open("users") as db:  # load user record from users database
                if str(user_id) in db:
                    user_record: defaultdict = db[str(user_id)]
                else:
                    user_record: defaultdict = defaultdict(None, {'last': deque(maxlen=10),
                                                                  'last_time': None})
                    db[str(user_id)] = user_record

            # catch bot slash-commands
            if text.startswith("/"):
                text = text.lower()[1:]
                if text == "start":
                    # '/start' command
                    raise ExitBatmanArea
                else:
                    # Unknown command
                    # feature! wrong slash-commands NOT deleted from chat
                    raise ExitBatmanArea

            # catch bot native commands (i.e. text)
            if command := text:
                if command.lower().startswith("last"):
                    # 'last' command
                    if dq_last := user_record['last']:
                        r = b.send_location(chat_id, lat=dq_last[0]['lat'], lng=dq_last[0]['lng'])
                        # mocking current message  msg
                        msg = r.json().get("result", {})
                    else:
                        b.send_textmessage(chat_id, "You have no saved requests yet.")
                else:
                    # Unknown text
                    # delete unsuitable message from user's chat
                    b.delete_message(chat_id, message_id)
                    raise ExitBatmanArea

            # cooldown check
            N = 1
            cooldown_delta = timedelta(minutes=N)
            now = Delorean.utcnow()
            if last_time := user_record['last_time']:
                if now >= last_time + cooldown_delta:
                    pass
                else:
                    b.send_textmessage(chat_id,
                                       f"There's a {N}-minute rest interval between each request")
                    raise ExitBatmanArea
            else:
                pass

            # location message check
            if not(lat := msg.get("location", {}).get("latitude")) or \
               not(lng := msg.get("location", {}).get("longitude")):
                # delete unsuitable message from user's chat
                b.delete_message(chat_id, message_id)
                raise ExitBatmanArea

            # live location check
            if msg.get("location", {}).get("live_period"):
                # send copy as static location
                b.send_location(chat_id, lat=lat, lng=lng)
                # delete original user's live location
                b.delete_message(chat_id, message_id)

            # == at this point pair (lat, lng) is trusted ==

            # send temporary "..." message to chat
            response = b.send_textmessage(chat_id, "...")
            assert response.ok, "Sending temporary message failed"
            temp_msg_id = response.json().get("result", {}).get("message_id", -1)  # -1 if failed

            # -- parse weather --
            current_weather_text, forecast_png = parseryrno.get_weather(lat, lng)
            # -- save request and time in the db --
            user_record['last'].appendleft({'lat': lat, 'lng': lng})  # min index -- most recent
            user_record['last_time'] = Delorean.utcnow()
            # -- send answer --
            b.reply_textmessage(chat_id, message_id, current_weather_text)
            b.send_photomessage(chat_id, forecast_png)

            # delete temporary "..." message
            # hint   temp_msg_id == -1   causes no exception and nothing deleted
            b.delete_message(chat_id, temp_msg_id)

            # update database
            with shelve.open("users") as db:
                db[str(user_id)] = user_record
