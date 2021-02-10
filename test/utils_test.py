# =============================================================================
# Twitwi Utilities Unit Tests
# =============================================================================
from pytz import timezone
from test.utils import get_json_resource

from twitwi.utils import get_dates, normalize_tweet

GET_DATES_TESTS = [
    (('Thu Feb 07 06:43:33 +0000 2013', 'Europe/Paris'), (1360219413, '2013-02-07T07:43:33')),
    (('Tue Nov 24 16:43:53 +0000 2020', 'Europe/Paris'), (1606236233, '2020-11-24T17:43:53')),
    (('Tue Nov 24 16:52:48 +0000 2020', 'Australia/Adelaide'), (1606236768, '2020-11-25T03:22:48'))
]


def compare_tweets(_id, t1, t2):
    for k in t2.keys():
        if k == 'collection_time':
            continue

        assert t1[k] == t2[k], 'Different value for key "%s" with tweet "%s"' % (k, _id)


class TestUtils(object):
    def test_get_dates(self):
        for (date_str, tz), result in GET_DATES_TESTS:
            tz = timezone(tz)

            assert get_dates(date_str, locale=tz) == result, (date_str, tz)

    def test_normalize_tweet(self):
        tz = timezone('Europe/Paris')

        tests = get_json_resource('normalization.json')

        for test in tests:
            result = normalize_tweet(
                test['source'],
                locale=tz,
                id_key='_id',
                extract_referenced_tweets=True
            )

            print([t['_id'] for t in result], [t['_id'] for t in test['normalized']])

            assert isinstance(result, list)
            assert len(result) == len(test['normalized'])

            for tweet in result:
                assert 'collection_time' in tweet and isinstance(tweet['collection_time'], str)

            for t1, t2 in zip(result, test['normalized']):
                compare_tweets(test['source']['id_str'], t1, t2)
