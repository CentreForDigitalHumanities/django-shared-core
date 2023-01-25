import logging
from datetime import datetime
from typing import Optional

from django.core.cache import BaseCache, cache as default_cache
from django.utils.timezone import get_current_timezone

from .resources import Token

logger = logging.getLogger('cdh.integration_platform.token_service')


class _TokenService:
    """Small singleton class that helps us manage token lifetimes with
    caching"""

    CACHE_KEY = 'integration_platform_token'

    def __init__(
            self,
            cache: Optional[BaseCache] = None,
            revoke_limit: int = 10
    ):
        logger.info('Creating TokenService')
        logger.debug(f'Revoke limit: {revoke_limit} seconds')
        self._cache = cache
        if self._cache is None:
            logger.debug(f'Using default Django cache: {default_cache}')
            self._cache: BaseCache = default_cache
        else:
            logger.debug(f'Using cache: {cache}')

        self._revoke_limit = revoke_limit

    def get_token(self):
        logger.info('Getting token')
        token = self._cache.get(self.CACHE_KEY)

        if token is None:
            logger.info('No token in cache, retrieving new one')
            token = self._request_token()
        else:
            token = Token(**token)
            logger.info(f'Using cached token {token}')

        if token is None:
            logger.critical('Could not get token!')
            return None

        if self._get_token_expiration(token) < self._revoke_limit:
            logger.info('Token will expire within revoke limit, revoking token')
            self._revoke_token(token)
            token = self._request_token()

        logger.info(f'Using token {token}')

        return token.access_token

    def _get_token_expiration(self, token: Token) -> int:
        return (token.expires_in - datetime.now(
            tz=get_current_timezone()
        )).total_seconds()

    def _request_token(self) -> Optional[Token]:
        try:
            logger.info(f'Fetching token')
            token = Token.client.get()
            logger.debug(f'Fetched {token}')

            seconds_till_expiry = self._get_token_expiration(token)

            logger.debug(f"Caching new token for "
                         f"{seconds_till_expiry} seconds")

            self._cache.set(
                self.CACHE_KEY,
                token.to_api(),
                seconds_till_expiry
            )
            logger.debug(f'Cached token')

            return token
        except Exception as e:
            logger.error(f'Error during token fetching: {e}')
            return None

    def _revoke_token(self, token: Token):
        try:
            logger.info(f'Revoking {token}')
            token.revoke()
            logger.debug(f'Revoked token')
        except Exception as e:
            logger.error(f'Error during token revocation: {e}')
        finally:
            logger.debug(f'Clearing cache')
            self._cache.delete(self.CACHE_KEY)


TokenService = _TokenService()
