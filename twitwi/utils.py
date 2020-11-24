# =============================================================================
# Twitwi Utilities
# =============================================================================
#
# Miscellaneous utility functions.
#
from datetime import datetime
from time import mktime
from pytz import timezone

from twitwi.constants import (
    TWEET_DATETIME_FORMAT,
    FORMATTED_TWEET_DATETIME_FORMAT
)

UTC_TIMEZONE = timezone('UTC')


def get_dates(date_str, locale=None):
    parsed_datetime = datetime.strptime(date_str, TWEET_DATETIME_FORMAT)
    utc_datetime = parsed_datetime
    locale_datetime = parsed_datetime

    if locale:
        utc_datetime = UTC_TIMEZONE.localize(parsed_datetime)
        locale_datetime = utc_datetime.astimezone(locale)

    return (
        utc_datetime.timestamp(),
        datetime.strftime(locale_datetime, FORMATTED_TWEET_DATETIME_FORMAT)
    )
