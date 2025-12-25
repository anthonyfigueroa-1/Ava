from zoneinfo import ZoneInfo
from datetime import datetime

from app import tz

def logs(message):
    mtn_zone = ZoneInfo(tz)
    now = datetime.now(tz=mtn_zone).strftime(format="%Y-%m-%d %H:%M:%S")
    print(f"{now} || {message}")
