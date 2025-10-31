from zoneinfo import ZoneInfo
from datetime import datetime

def logs(log):
    mtn = ZoneInfo("America/Denver")
    now = datetime.now(tz=mtn).strftime("%m-%d-%Y %H:%M:%S")

    text = f"{now} || {log}"
    print(text)
