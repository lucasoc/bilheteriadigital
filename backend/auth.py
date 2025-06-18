from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "sua_chave_super_secreta"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30
auth_scheme = HTTPBearer()

def criar_token(data: dict):
    expira = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expira})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

async def lambdaAuthorizer(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    return verificar_token(credentials.credentials)
