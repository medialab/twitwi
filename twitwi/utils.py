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
    CANONICAL_HOSTNAME_KWARGS,
    PRE_SNOWFLAKE_LAST_TWEET_ID,
    OFFSET_TIMESTAMP,
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

    if 'data' not in payload:
        if 'meta' in payload and 'result_count' in payload['meta'] and payload['meta']['result_count'] == 0:
            return True
        else:
            return False

    if not isinstance(payload['data'], list):
        return False

    # NOTE: not sure it cannot be absent altogether
    if 'includes' not in payload or not isinstance(payload['includes'], dict):
        return False

    return True


def get_timestamp_from_id(tweet_id):
    tweet_id = int(tweet_id)

    if tweet_id > PRE_SNOWFLAKE_LAST_TWEET_ID:
        timestamp = (tweet_id >> 22) + OFFSET_TIMESTAMP
        return int(timestamp / 1000)

    return None


def get_dates_from_id(tweet_id, locale=None):
    if locale is None:
        locale = UTC_TIMEZONE

    timestamp = get_timestamp_from_id(tweet_id)

    locale_datetime = datetime.fromtimestamp(timestamp, locale)

    return (timestamp, datetime.strftime(locale_datetime, FORMATTED_TWEET_DATETIME_FORMAT))
