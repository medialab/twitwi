# =============================================================================
# Twitwi Utilities
# =============================================================================
#
# Miscellaneous utility functions.
#
from pytz import timezone
from ural import normalize_url, get_normalized_hostname
from functools import partial
from datetime import datetime

from twitwi.constants import (
    TWEET_DATETIME_FORMAT,
    FORMATTED_TWEET_DATETIME_FORMAT,
    TWEET_DATETIME_FORMAT_V2,
    CANONICAL_URL_KWARGS,
    CANONICAL_HOSTNAME_KWARGS
)

UTC_TIMEZONE = timezone('UTC')

custom_normalize_url = partial(
    normalize_url,
    **CANONICAL_URL_KWARGS
)

custom_get_normalized_hostname = partial(
    get_normalized_hostname,
    **CANONICAL_HOSTNAME_KWARGS
)


def get_dates(date_str, locale=None, v2=False):
    if locale is None:
        locale = UTC_TIMEZONE

    parsed_datetime = datetime.strptime(date_str, TWEET_DATETIME_FORMAT_V2 if v2 else TWEET_DATETIME_FORMAT)
    utc_datetime = UTC_TIMEZONE.localize(parsed_datetime)
    locale_datetime = utc_datetime.astimezone(locale)

    return (
        int(utc_datetime.timestamp()),
        datetime.strftime(locale_datetime, FORMATTED_TWEET_DATETIME_FORMAT)
    )


def validate_payload_v2(payload):
    if not isinstance(payload, dict):
        return False

    if 'data' not in payload or not isinstance(payload['data'], list):
        return False

    # NOTE: not sure it cannot be absent altogether
    if 'meta' not in payload or not isinstance(payload['meta'], dict):
        return False

    # NOTE: not sure it cannot be absent altogether
    if 'includes' not in payload or not isinstance(payload['includes'], dict):
        return False

    return True
