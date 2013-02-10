"""
Defaults and standard values for various settings used 
in the YSports module.
"""
import logging


## Defaults
DFT_AUTH_FILE = 'ysports/cache/tokensecrets.csv'
LOG_FILENAME = 'ysports/cache/ysports.log'
INTERACTIVE_AUTHORIZATION = True

## Logging
LOGGING_LEVEL = logging.INFO
TOKEN_EXPIRATION_TIME = 3540 ## one hour, minus one minute for leeway
logging.basicConfig(filename=LOG_FILENAME,
                    format='%(asctime)s  %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=LOGGING_LEVEL)

## Yahoo URLs
REQUEST_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
AUTH_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_token'
YQL_ENDPOINT = 'http://query.yahooapis.com/v1/yql'
DFT_LEAGUE_KEY = 'nfl.l.000000'
