"""

String templates, text for locales (in the future), environment variable for parser

"""
import dotenv
from os import getenv
dotenv.load_dotenv()

# timezone.db API key default
TIMEDB_KEY = None
if getenv("TIMEDB_KEY") and getenv("TIMEDB_KEY") != "timedbkey":
    TIMEDB_KEY = getenv("TIMEDB_KEY")

# scale by default (has effect only on Linux)
SCALE = 0.8
if getenv("SCALE"):
    SCALE = float(getenv("SCALE"))


TIMEDB_API_URL = "http://api.timezonedb.com/v2.1/get-time-zone?key={}&format=json&by=position&lat={}&lng={}"
TIMEDB_API_TEST_URL = "http://api.timezonedb.com/v2.1/list-time-zone?key={}&format=json&zone=Asia/Tokyo&fields=zoneName"

YR_URL = "https://www.yr.no"
YR_FORECAST_URL = "https://www.yr.no/en/forecast/daily-table/{},{}"
YR_METEOGRAM_URL = "https://www.yr.no/en/content/{},{}/meteogram.svg"



