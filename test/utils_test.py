# =============================================================================
# Twitwi Utilities Unit Tests
# =============================================================================
from functools import partial
from pytz import timezone
from copy import deepcopy
from test.utils import get_json_resource

from twitwi.utils import (
    get_dates,
    normalize_tweet,
    normalize_user,
    normalize_tweets_payload_v2
)

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
        fn = partial(normalize_tweet, locale=tz)

        # With referenced tweets
        for test in tests:
            result = fn(test['source'], extract_referenced_tweets=True)

            assert isinstance(result, list)
            assert set(t['id'] for t in result) == set(t['id'] for t in test['normalized'])

            for tweet in result:
                assert 'collection_time' in tweet and isinstance(tweet['collection_time'], str)

            for t1, t2 in zip(result, test['normalized']):
                compare_tweets(test['source']['id_str'], t1, t2)

        # With single output
        for test in tests:
            tweet = fn(test['source'])

            assert isinstance(tweet, dict)

            _id = test['source']['id_str']
            compare_tweets(_id, tweet, next(t for t in test['normalized'] if t['id'] == _id))

        # With custom collection_source
        for test in tests:
            tweet = fn(test['source'], collection_source='unit_test')

            assert tweet['collected_via'] == ['unit_test']

    def test_normalize_tweet_should_not_mutate(self):
        tweet = get_json_resource('normalization.json')[0]['source']

        original_arg = deepcopy(tweet)

        ntweet = normalize_tweet(tweet)

        assert tweet == original_arg

    def test_normalize_user(self):
        tz = timezone('Europe/Paris')

        api_users = get_json_resource('api-users-v1.json')

        normalized_users = [normalize_user(user, locale=tz) for user in api_users]

        # with open('./test/resources/normalized-users.json', 'w') as f:
        #     import json
        #     json.dump(normalized_users, f, ensure_ascii=False, indent=2)

        assert normalized_users == get_json_resource('normalized-users.json')

    def test_normalize_user_should_not_mutate(self):
        user = get_json_resource('api-users-v1.json')[0]

        original_arg = deepcopy(user)

        nuser = normalize_user(user)

        assert user == original_arg

    def test_normalize_tweets_payload_v2(self):
        payload = get_json_resource('payload_v2.json')

        tweets = normalize_tweets_payload_v2(payload)

        # print()
        # for t in tweets:
        #     print(t)
        # print()
