import botobject
import dotenv

dotenv_template = \
'''# Place here token got from telegram bot "BotFather"
#
TELEGRAM_BOT_TOKEN="{telegram_token}"

# If you want to see local time at the requested places,
# place here token from timezonedb.com
# It can be easily obtained after registration
#
TIMEDB_KEY="{timedb_key}"


# Meteogram image internal scaling before sending to Telegram
# (poor internet connection causes output size to become significant)
# 0.8 => 45kb jpeg in the client chat, blurry but still distinct
# 1 => 65kb jpeg
# 2 => 165kb jpeg
#
SCALE="{png_scale}"
'''

config = dotenv.dotenv_values(".env")
if config:
    print('Config file  ".env"  found.\n'
          'Do you want to reset it?')
    if input("(y/N)?") != "y":
        print('You can set variables up at any time by editing text of ".env" file')
        exit()
    else:
        pass
else:
    print('No config file found! \n'
          'File  ".env"  to be created')

tbt = input("\n"
            "Paste telegram bot token here:\n"
            ">")
# Check token
b = botobject.Bot(tbt)
if b.username:
    print(f"OK - valid token\n"
          f"Username:{b.username}")
else:
    print("Token invalid!\n"
          "Restart setup.py and paste the valid token that you have recieved from Telegram BotFather")
    exit()
tdk = input("\nEnter timezonedb.com key or leave empty:\n>")
print("This key isn't beign checked yet")

pns = input("\nEnter meteogram scale or leave empty (default=0.8):\n>")
try:
    float(pns)
except:
    print("Value not acceptable. Default scale factor will be used")
    pns = ""
else:
    print("OK - valid value")

dotenv_string = dotenv_template.format(telegram_token=tbt,
                                       timedb_key=tdk if tdk else "timedbkey",
                                       png_scale=pns if pns else "0.8")
print(f"You  .env  file will look like this:\n")
print("-"*10)
print(dotenv_string)
print("-"*10)
if input("Save (y/N)? ").lower() == "y":
    with open(".env", "w") as f:
        f.write(dotenv_string)
    print("Done!")
    exit()
else:
    print("Setup was not finished.")
    exit()
