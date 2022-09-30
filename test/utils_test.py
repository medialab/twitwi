# =============================================================================
# Twitwi Utilities Unit Tests
# =============================================================================
from pytz import timezone
from test.utils import get_json_resource

from twitwi.utils import (
    get_dates,
    get_timestamp_from_id,
    validate_payload_v2
)

GET_DATES_TESTS = [
    (('Thu Feb 07 06:43:33 +0000 2013', 'Europe/Paris'), (1360219413, '2013-02-07T07:43:33')),
    (('Tue Nov 24 16:43:53 +0000 2020', 'Europe/Paris'), (1606236233, '2020-11-24T17:43:53')),
    (('Tue Nov 24 16:52:48 +0000 2020', 'Australia/Adelaide'), (1606236768, '2020-11-25T03:22:48'))
]

GET_TIMESTAMP_TESTS = [(1479161354066051075, 1641494522), (1503824656331165704, 1647374712), (1487215657854795777, 1643414818)]


class TestUtils(object):
    def test_get_dates(self):
        for (date_str, tz), result in GET_DATES_TESTS:
            tz = timezone(tz)

            assert get_dates(date_str, locale=tz) == result, (date_str, tz)

    def test_validate_payload_v2(self):
        assert not validate_payload_v2('hello')
        assert not validate_payload_v2([1, 2, 3])
        assert not validate_payload_v2({'meta': {}})
        assert validate_payload_v2(get_json_resource('payload-v2.json'))

    def test_get_timestamp_from_id(self):
        for id, result in GET_TIMESTAMP:
            assert get_timestamp_from_id(id) == result
