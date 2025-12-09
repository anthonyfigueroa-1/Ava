from zoneinfo import ZoneInfo
from datetime import datetime

def logs(log: str, log_type=None) -> None:
    mtn = ZoneInfo("America/Denver")
    now = datetime.now(tz=mtn).strftime("%m-%d-%Y %H:%M:%S")

    if log_type:
        log_type = log_type.lower()

        match log_type:
            case "info":
                text = f"{now} || INFO || {log}"
            case "error":
                text = f"{now} || ERROR || {log}"
            case _:
                text = f"{now} || {log}"
    else:
        text = f"{now} || {log}"

    print(text)
