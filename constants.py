import datetime
from pathlib import Path

DATE_FORMAT = '%d_%m_%Y'
DATE_TODAY: str = datetime.date.today().strftime(DATE_FORMAT)
RESULS_DIR = 'results'
BASE_DIR = Path(__file__).parent
BAD_WORDS = ['врач', 'преподаватель', 'репетитор', 'автор',]
WEB_DRIVER_DIR = 'chromedriver'
LOGIN_URL = 'https://hh.ru/account/login'
WEB_DRIVER_PATH = BASE_DIR / WEB_DRIVER_DIR / 'chromedriver.exe'
PARSE_PAUSE = 60 * 5
MAX_PARSE = 201
