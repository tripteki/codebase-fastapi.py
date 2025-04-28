from datetime import datetime, timedelta
from typing import Dict, Optional
import bcrypt
from jose import jwt, JWTError
from src.app.bases.app_context import AppContext
from src.app.configs.auth_config import AuthConfig

class AppAuth:
    """
    AppAuth
    """
    @classmethod
    def config (cls) -> AuthConfig:
        """
        Args:
            cls
        Returns:
            AuthConfig
        """
        return AuthConfig.config ()

    @classmethod
    def hashPassword (cls, password: str) -> str:
        """
        Args:
            password (str)
        Returns:
            str
        """
        salt = bcrypt.gensalt ()
        hashed = bcrypt.hashpw (password.encode ('utf-8'), salt)
        return hashed.decode ('utf-8')

    @classmethod
    def verifyPassword (cls, plainPassword: str, hashedPassword: str) -> bool:
        """
        Args:
            plainPassword (str)
            hashedPassword (str)
        Returns:
            bool
        """
        try:
            return bcrypt.checkpw (plainPassword.encode ('utf-8'), hashedPassword.encode ('utf-8'))
        except Exception:
            return False

    @classmethod
    def createAccessToken (cls, data: Dict[str, object], expiresDelta: Optional[timedelta] = None) -> str:
        """
        Args:
            data (Dict[str, object])
            expiresDelta (Optional[timedelta])
        Returns:
            str
        """
        config = cls.config ()
        toEncode = data.copy ()
        if expiresDelta:
            expire = datetime.utcnow () + expiresDelta
        else:
            expire = datetime.utcnow () + timedelta (minutes=config.jwt_access_token_expire_minutes)
        toEncode.update ({
            "exp": expire,
            "iat": datetime.utcnow (),
            "type": "access"
        })
        if config.jwt_issuer:
            toEncode["iss"] = config.jwt_issuer
        if config.jwt_audience:
            toEncode["aud"] = config.jwt_audience
        encodedJwt = jwt.encode (toEncode, config.jwtSecret (), algorithm=config.jwt_algorithm)
        return encodedJwt

    @classmethod
    def createRefreshToken (cls, data: Dict[str, object]) -> str:
        """
        Args:
            data (Dict[str, object])
        Returns:
            str
        """
        config = cls.config ()
        toEncode = data.copy ()
        expire = datetime.utcnow () + timedelta (days=config.jwt_refresh_token_expire_days)
        toEncode.update ({
            "exp": expire,
            "iat": datetime.utcnow (),
            "type": "refresh"
        })
        if config.jwt_issuer:
            toEncode["iss"] = config.jwt_issuer
        if config.jwt_audience:
            toEncode["aud"] = config.jwt_audience
        encodedJwt = jwt.encode (toEncode, config.jwtSecret (), algorithm=config.jwt_algorithm)
        return encodedJwt

    @classmethod
    def verifyToken (cls, token: str, tokenType: str = "access") -> Optional[Dict[str, object]]:
        """
        Args:
            token (str)
            tokenType (str)
        Returns:
            Optional[Dict[str, object]]
        """
        config = cls.config ()
        try:
            payload = jwt.decode (
                token,
                config.jwtSecret (),
                algorithms=[config.jwt_algorithm],
                issuer=config.jwt_issuer if config.jwt_issuer else None,
                audience=config.jwt_audience if config.jwt_audience else None
            )
            if payload.get ("type") != tokenType:
                return None
            return payload
        except JWTError:
            return None

    @classmethod
    def decodeToken (cls, token: str) -> Optional[Dict[str, object]]:
        """
        Args:
            token (str)
        Returns:
            Optional[Dict[str, object]]
        """
        try:
            config = cls.config ()
            payload = jwt.decode (
                token,
                config.jwtSecret () or "",
                algorithms=[config.jwt_algorithm],
                options={
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_iss": False,
                    "verify_aud": False
                }
            )

            return payload
        except (JWTError, Exception):
            return None

    @classmethod
    async def isTokenBlacklisted (cls, token: str) -> bool:
        """
        Args:
            token (str)
        Returns:
            bool
        """
        try:
            cacheRedis = AppContext.cacheRedis ()
            if not cacheRedis:
                return False
            key = f"blacklist:token:{token}"
            result = await cacheRedis.get (key)
            return result is not None
        except Exception:
            return False

    @classmethod
    async def blacklistToken (cls, token: str, ttl: Optional[int] = None) -> bool:
        """
        Args:
            token (str)
            ttl (Optional[int])
        Returns:
            bool
        """
        try:
            cacheRedis = AppContext.cacheRedis ()
            if not cacheRedis:
                return False
            key = f"blacklist:token:{token}"
            if ttl is None:
                payload = cls.decodeToken (token)
                if payload and "exp" in payload:
                    exp = payload["exp"]
                    now = int (datetime.utcnow ().timestamp ())
                    ttl = max (0, exp - now)
                else:
                    config = cls.config ()
                    ttl = config.jwt_access_token_expire_minutes * 60
            if ttl > 0:
                await cacheRedis.setex (key, ttl, "1")
                return True
            return False
        except Exception:
            return False
