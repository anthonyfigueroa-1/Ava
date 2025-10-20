from zoneinfo import ZoneInfo
from datetime import datetime

def new_log_file():
    with open("/logs/logs.txt", "w") as file:
        pass

def logs(log):
    mtn = ZoneInfo("America/Denver")
    now = datetime.now(tz=mtn).strftime("%m-%d-%Y %H:%M:%S")

    text = f"{now} || {log}"
    print(text)

    with open("/logs/logs.txt", "a") as file:
        file.write(text + "\n")
