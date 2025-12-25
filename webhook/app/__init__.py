from dotenv import load_dotenv
import os
load_dotenv()

tz = os.getenv("TZ", "America/Denver")
