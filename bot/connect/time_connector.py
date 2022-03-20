import pytz
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()


def convert_utc_to_local(utc_dt):
    utc_dt = datetime.strptime(utc_dt, '%Y-%m-%d %H:%M:%S')
    local_tz = pytz.timezone(os.environ['timezone'])
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)
