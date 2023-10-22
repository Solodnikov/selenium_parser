import datetime
from pathlib import Path

DATE_FORMAT = '%d_%m_%Y'
DATE_TODAY: str = datetime.date.today().strftime(DATE_FORMAT)
RESULS_DIR = 'results'
BASE_DIR = Path(__file__).parent
BAD_WORDS = ['врач', 'преподаватель']