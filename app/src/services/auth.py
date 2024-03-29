import logging
from datetime import datetime, timezone
from uuid import UUID

import aiohttp
import backoff
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import decode

from core.config import settings
from db import redis


logger = logging.getLogger(__name__)


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> UUID:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme.")

            payload = await self.get_payload(credentials.credentials)
            check_auth = await self.check_auth(token=credentials.credentials, payload=payload)
            if not check_auth:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Auth: Invalid token or expired token.")

            return payload.get('sub')

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization code.")

    @staticmethod
    async def get_payload(token: str) -> dict:
        """
        Если токен валидный и не истек срок его действия, то возвращает данные токена

        :param token: Токен для проверки
        :return: Данные из токена в виде словаря
        """
        try:
            payload = decode(token, options={"verify_signature": False})
            sub = UUID(payload.get('sub'))
            if payload.get("exp") > datetime.now(timezone.utc).timestamp():
                return payload
        except Exception:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token.")

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Expired token.")

    @backoff.on_exception(backoff.expo, aiohttp.ClientError)
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

    @staticmethod
    async def _jwt_from_cache(jti: UUID) -> bool:
        return await redis.client.get(str(jti))

    @staticmethod
    async def _put_jwt_to_cache(payload: dict, value: bool):
        ex = settings.cache_expire
        if payload.get("exp") - datetime.now(timezone.utc).timestamp() < ex:
            ex = payload.get("exp") - datetime.now(timezone.utc).timestamp()

        await redis.client.set(payload.get('jti'), int(value), ex)


bearer = JWTBearer()
