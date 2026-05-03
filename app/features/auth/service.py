import bcrypt
import jwt
import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from app.core.config import Settings

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._secret = getattr(settings, "jwt_secret", "velra_super_secret_key_change_me")
        self._algorithm = "HS256"
        logger.debug("AuthService initialized")

    def get_password_hash(self, password: str) -> str:
        # bcrypt.hashpw expects bytes
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pwd_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)

    def create_access_token(self, subject: str | Any, expires_delta: timedelta | None = None) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=60*24) # 24h default
            
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, self._secret, algorithm=self._algorithm)
        return encoded_jwt

    def decode_access_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
