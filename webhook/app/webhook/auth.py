from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import os, sys

security = HTTPBearer()
key = os.getenv("API_KEY")

if not key:
    sys.exit(1)

def check_token(creds: HTTPAuthorizationCredentials = Depends(security)):
    if creds:
        if creds.credentials != key:
            raise HTTPException(status_code=403, detail="Invalid token")
