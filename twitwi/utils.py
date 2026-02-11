# =============================================================================
# Twitwi Utilities
# =============================================================================
#
# Miscellaneous utility functions.
#
from typing import Tuple

from pytz import timezone
from dateutil.parser import parse as parse_date
from ural import normalize_url, get_normalized_hostname
from functools import partial
from datetime import datetime

from twitwi.constants import (
    SOURCE_DATETIME_FORMAT,
    SOURCE_DATETIME_FORMAT_V2,
    FORMATTED_TWEET_DATETIME_FORMAT,
    FORMATTED_FULL_DATETIME_FORMAT,
    CANONICAL_URL_KWARGS,
    CANONICAL_HOSTNAME_KWARGS,
    PRE_SNOWFLAKE_LAST_TWEET_ID,
    OFFSET_TIMESTAMP,
)

UTC_TIMEZONE = timezone("UTC")

custom_normalize_url = partial(normalize_url, **CANONICAL_URL_KWARGS)


def safe_normalize_url(url):
    # We avoid normalizing bluesky urls containing specific uri parts because
    # Bluesky servers don't handle quoting correctly...
    # See https://github.com/medialab/twitwi/issues/72
    if "/did:plc:" in url:
        return url

    try:
        return custom_normalize_url(url)
    except Exception:
        # In case of error, return the original URL. Possibly not a valid URL, e.g. url containing double slashes
        return url


custom_get_normalized_hostname = partial(
    get_normalized_hostname, **CANONICAL_HOSTNAME_KWARGS
)


def get_collection_time():
    return datetime.now().strftime(FORMATTED_FULL_DATETIME_FORMAT)


def get_dates(
    date_str: str, locale=None, source: str = "v1", millisecond_timestamp: bool = False
) -> Tuple[int, str]:
    if source not in ["v1", "v2", "no_api_key", "bluesky"]:
        raise Exception("source should be one of v1, v2, no_api_key or bluesky")

    if locale is None:
        locale = UTC_TIMEZONE

    # Let's pray we never see a negative year...
    year_zero = date_str.startswith("0000") or all(
        c == "0" for c in date_str.split("-")[0]
    )

    try:
        parsed_datetime = datetime.strptime(
            date_str,
            SOURCE_DATETIME_FORMAT if source == "v1" else SOURCE_DATETIME_FORMAT_V2,
        )
    except ValueError as e:
        if source != "bluesky":
            raise e
        # Yes, it seems that some people were active in year 0...
        # see by yourself: https://bsky.app/profile/koro.icu/post/3kbpuogc6fz2o
        if year_zero:
            date_str_fixed = "0001" + date_str[4:]
            parsed_datetime = parse_date(date_str_fixed)
        else:
            parsed_datetime = parse_date(date_str)

    utc_datetime = parsed_datetime
    if not parsed_datetime.tzinfo:
        utc_datetime = UTC_TIMEZONE.localize(parsed_datetime)
    locale_datetime = utc_datetime.astimezone(locale)

    formatted_date_str = datetime.strftime(
        locale_datetime,
        FORMATTED_FULL_DATETIME_FORMAT
        if source == "bluesky"
        else FORMATTED_TWEET_DATETIME_FORMAT,
    )

    timestamp = int(utc_datetime.timestamp())

    if year_zero:
        # Subtract one year (year 0001 is not a leap year) in seconds
        timestamp -= 31536000
        # Doing like so using split because on ubuntu, datetime.strftime on year with less than 4 digits
        # only returns 1 digit for year 0 (e.g. "0-05-12...") instead of 4 digits ("0000-05-12..."),
        # whereas on macOS and Windows it returns 4 digits.
        formatted_date_str = "0000-" + formatted_date_str.split("-", 1)[1]

    if millisecond_timestamp:
        timestamp *= 1000
        timestamp += utc_datetime.microsecond / 1000

    return (
        int(timestamp),
        formatted_date_str,
    )


def validate_payload_v2(payload):
    if not isinstance(payload, dict):
        return False

    if "data" not in payload:
        if (
            "meta" in payload
            and "result_count" in payload["meta"]
            and payload["meta"]["result_count"] == 0
        ):
            return True
        else:
            return False

    if not isinstance(payload["data"], list):
        return False

    # NOTE: not sure it cannot be absent altogether
    if "includes" not in payload or not isinstance(payload["includes"], dict):
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
    assert timestamp is not None

    locale_datetime = datetime.fromtimestamp(timestamp, locale)

    return (
        timestamp,
        datetime.strftime(locale_datetime, FORMATTED_TWEET_DATETIME_FORMAT),
    )

def format_profile_url(user_screen_name):
    return f"https://twitter.com/{user_screen_name}"