# =============================================================================
# Twitwi Utilities Unit Tests
# =============================================================================
from pytz import timezone
from test.utils import get_json_resource

from twitwi.utils import (
    get_dates
)

GET_DATES_TESTS = [
    (('Thu Feb 07 06:43:33 +0000 2013', 'Europe/Paris'), (1360219413, '2013-02-07T07:43:33')),
    (('Tue Nov 24 16:43:53 +0000 2020', 'Europe/Paris'), (1606236233, '2020-11-24T17:43:53')),
    (('Tue Nov 24 16:52:48 +0000 2020', 'Australia/Adelaide'), (1606236768, '2020-11-25T03:22:48'))
]


class TestUtils(object):
    def test_get_dates(self):
        for (date_str, tz), result in GET_DATES_TESTS:
            tz = timezone(tz)

            assert get_dates(date_str, locale=tz) == result, (date_str, tz)
