from zoneinfo import ZoneInfo
from datetime import datetime

def logs(log: str) -> None:
    mtn_zone = ZoneInfo("America/Denver")
    now_mtn = datetime.now(tz=mtn_zone)
    now_mtn = now_mtn.strftime("%m-%d-%Y %H:%M:%S")

    print(f"{now_mtn} || {log}")
