"""

Forecast site parser

"""
# custom imports
import vars
from svg2png import svg2png

import requests
import traceback
from bs4 import BeautifulSoup
from time import sleep


def get_weather(lat, lng):
    if not(lat and lng):
        return "Wrong location given", None

    # TO SOUP prepare   yr_forecast_page
    yr_forecast_page = requests.get(vars.YR_FORECAST_URL.format(lat, lng)).text
    soup = BeautifulSoup(yr_forecast_page, "html.parser")
    tag_currw = soup.find('div', class_='now-hero__next-hour-content')  # soup for "current weather"

    # PARSE "current weather" block
    tag_currw_t = tag_currw.find('span', class_='temperature')  # temperature <span>
    tag_currw_at = tag_currw.find('div', class_='feels-like-text')  # feels like <div>
    # INTERPRET to variables
    text_temp = tag_currw_t.get_text().replace('Temperature', 'Temperature ')  # temperature
    text_feelslike = tag_currw_at.get_text()  # feels like temperarure

    # Jan 2023 fix
    tag_currw_nexthourtexts = tag_currw.findAll('div', class_='now-hero__next-hour-text')
    # precipitation (mm) by text
    text_precipitation = " ".join([t.get_text()
                                   for t
                                   in tag_currw_nexthourtexts[1].select("span")[0].findAll()])
    text_precipitation = text_precipitation.replace("  ", " ")
    # # wind by text
    text_wind = tag_currw_nexthourtexts[2].select("span")[0].find("span").get_text()

    text_clouds = soup.find(class_="daily-weather-list-item__symbols"). \
        findChild(class_="weather-symbol__img")['alt']. \
        split(": ")[-1]

    # GET weather forecast meteogram in SVG format and convert to PNG
    b_meteogram_png = None
    try:
        response = requests.get(vars.YR_METEOGRAM_URL.format(lat, lng))  # fetch SVG
        b_meteogram_png = svg2png(response.text.encode())  # bytes from response to bytes png
    except Exception:
        print("Meteogram obtaining failed")
        print("-----traceback:-----\n", traceback.format_exc())
        print("--------------------")

    # GET local datetime from timezonedb.com
    local_datetime = ""
    if vars.TIMEDB_KEY:
        if requests.get(vars.TIMEDB_API_TEST_URL.format(vars.TIMEDB_KEY)).json()["status"] == "OK":
            timedb_api_url = vars.TIMEDB_API_URL.format(vars.TIMEDB_KEY, lat, lng)
            local_datetime = requests.get(timedb_api_url).json()["formatted"]  # get local datetime
            sleep(0.5)  # observe the recommendation of timedb api about polling frequency

    # FORMAT resulting text message
    s_res = (f"<i>📍 {lat}, {lng}\n"
             f"{'🕔' if local_datetime else ' '} {local_datetime}\n</i>"
             f"<pre>Current weather conditions:\n"
             f"-> {text_clouds if text_clouds is not None else ' '}\n"
             f"-> {text_temp if text_temp is not None else ' '}\n"
             f"-> {text_feelslike if text_feelslike is not None else ' '}\n"
             f"-> {text_precipitation if text_precipitation is not None else ' '}\n"
             f"-> {text_wind if text_wind is not None else ' '} </pre>\n"
             f"\t\t\n")
    s_res += r'<a href="{}">[𝕊𝔼𝔼 𝔽𝕆ℝ𝔼ℂ𝔸𝕊𝕋 𝕆ℕ 𝕋ℍ𝔼 𝕊𝕀𝕋𝔼]</a>'.format(
        vars.YR_FORECAST_URL.format(lat, lng))
    return s_res, b_meteogram_png
