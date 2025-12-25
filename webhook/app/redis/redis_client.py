from redis import RedisError
#uuid is for generating unique/random uuid's
from uuid import uuid4
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import HTTPException
import json

from app import tz
from app.logs import logs
from app.redis import redis
from app.redis.queue_duplicate import queue_duplicate

mtn_zone = ZoneInfo(tz)

def send_queue(ticket, job_type):
    is_new = queue_duplicate(ticket, job_type)
    if is_new is True:
        #pipe allows me to create a chain of commands to push to redis as to avoid partial commands in case of script failing
        pipe = redis.pipeline()
        id = str(uuid4())
        job_id = f"jobs:{id}"
        job = {
                "recieved_at": datetime.now(tz=mtn_zone).isoformat(timespec="seconds"),
                "status": "queued",
                "type": job_type,
                "ticket": json.dumps(ticket),
                }

        try:
            #hset is for setting hash, or json. Cannot store json inside of a hashvalue. Json must be converted to str().
            pipe.hset(job_id, mapping=job)
            #experation for hash as the only way to get to hash it by the uuid, if uuid is unkown, hash exists 'forever'. So we set them to expire.
            pipe.expire(job_id, 86400)
            pipe.lpush("jobs", job_id)
            pipe.execute()

            logs(f"JOB '{job_id}' sent to queue")
        except RedisError as e:
            raise HTTPException(503, f"Redis error: {e}")

    else:
        logs(f"Request is a duplicate, not sending to queue")
