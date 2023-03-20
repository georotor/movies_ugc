from datetime import datetime, timezone
from uuid import UUID

import aiohttp
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import decode

from core.config import settings
from db.redis import redis


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> UUID:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme.")

            payload = await self.verify_jwt(credentials.credentials)
            if not payload:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token or expired token.")

            check_auth = await self.check_auth(token=credentials.credentials, payload=payload)
            if not check_auth:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Auth: Invalid token or expired token.")

            return payload.get('sub')

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization code.")

    @staticmethod
    async def get_payload(token: str) -> dict:
        return decode(token, options={"verify_signature": False})

    async def check_auth(self, token: str, payload: dict) -> bool:
        """
        Проверяем валидность в токена во внешнем сервисе и кэшируем результат

        :param token: Токен
        :param payload: Данные из токена
        """
        if not settings.jwt_validate:
            return True

        cache = await self._jwt_from_cache(payload.get('jti'))
        if cache is not None:
            return bool(int(cache))

        res = False

        session = aiohttp.ClientSession()
        async with session.get(settings.auth_url, headers={'Authorization': f'Bearer {token}'}) as auth_response:
            if auth_response.status == status.HTTP_200_OK:
                res = True
            await self._put_jwt_to_cache(payload, res)

            return res

    async def verify_jwt(self, token: str) -> dict | bool:
        """
        Проверяет что в токене есть данные и его срок годности не истек

        :param token: Токен для проверки
        :return: Данные из токена в виде словаря или False
        """
        try:
            payload = await self.get_payload(token)
            if payload.get("exp") > datetime.now(timezone.utc).timestamp():
                return payload
        except:
            return False

        return False

    async def _jwt_from_cache(self, jti: UUID) -> bool:
        return await redis.get(str(jti))

    async def _put_jwt_to_cache(self, payload: dict, value: bool):
        ex = settings.cache_expire
        if payload.get("exp") - datetime.now(timezone.utc).timestamp() < ex:
            ex = payload.get("exp") - datetime.now(timezone.utc).timestamp()

        await redis.set(payload.get('jti'), int(value), ex)
