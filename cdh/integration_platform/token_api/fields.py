from datetime import datetime, timedelta
from typing import Union

from django.utils.timezone import get_current_timezone

from cdh.rest.client import fields
from cdh.rest.client.logging import field_logger as logger


class ExpiryField(fields.DateTimeField):

    def to_python(self, value: Union[str, int]) -> datetime:
        """Custom datetime field which will transform the API's expiry in
        seconds to a datetime.

        This way we can cache the token, and know _exactly_ when the token is
        supposed to expire when we retrieve the token from the cache.
        """
        if isinstance(value, int):
            logger.debug(f"{repr(self)}: Transforming seconds to datetime:"
                         f" {repr(value)}")
            value = datetime.now(
                tz=get_current_timezone()
            ) + timedelta(seconds=value)
            logger.debug(f"{repr(self)}: result: {repr(value)}")

            return value

        return super().to_python(value)  # NoQA, linter doesn't get this typing
