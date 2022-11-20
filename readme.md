# scandi-geoweather-bot
Just another Telegram weather bot which uses specific Norvegian forecast service to deliver weather forecast for TG-location. 

### Project
The bot was developed for the one private northern guide and emergency service. Customer's version has advantage in ability of reverse geocoding (can get forecast of locality by name), more than one last message to repeat request and has no cooldown restrictions.

### Features and restrictions
Output picture can be configured to a very small filesize in order to elusive internet connection in a mountains. Moreover Telegram itself is a very tenacious service, it can deliver messages over a very poor connection. You can send request for weather in last N geopoints(last one in public releаse) with no internet at all, than having a result fetched by TG in a random places of your route for example on the upcoming mountain pass.

Most accurate results can be reached only in Norvegian, Swedish, Finnish and Russian Kolsky peninsulla regions. 

No forecast povider's API used, html parsed instead.


### Simplest logic
1. Get all new messages from TG API to Bot /bare requests used/
2. Process every message:
   * Check bot commands with slash
   * Check bot commands given as text
   * Recognise "last *N*" ("last") command to process previously requested locations.
   * Check for cooldown time (1 minute)
   * Filter messages, that has location fields, transform live locations. 
   * Parse weather if all ok:
       1. Get local time at the point ("lat,lng" got from given location), current weather condition and forecast (SVG converted to PNG) from parser
       2. Compose text and picture
   * Send answer to message
3. If something went wrong, just ignore and make shure to stay alive
4. Repeat forever

### Released
`@scandi_geoweather_bot` is deployed on my server and it's exactly the same as this repo.

Bot uptime since first beta in December 2020. [Try in Telegram](https://t.me/scandi_geoweather_bot)
