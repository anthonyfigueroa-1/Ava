from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def check_token(creds: HTTPAuthorizationCredentials = Depends(security)):
    if creds:
        if creds.credentials != "Pock":
            raise HTTPException(status_code=403, detail="Invalid token")
