# =============================================================================
# Twitwi Utilities Unit Tests
# =============================================================================
import pytest
from functools import partial
from pytz import timezone
from copy import deepcopy
from ebbe import sorted_uniq
from operator import itemgetter
from test.utils import get_json_resource

from twitwi.normalizers import (
    normalize_tweet,
    normalize_user,
    normalize_tweets_payload_v2
)


def compare_tweets(_id, t1, t2):
    for k in t2.keys():
        if k == 'collection_time':
            continue

        assert t1[k] == t2[k], 'Different value for key "%s" with tweet "%s"' % (k, _id)

    for k in t1.keys():
        assert k in t2, 'Missing key "%s" with tweet "%s"' % (k, _id)


class TestNormalizers(object):
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

        # from test.utils import dump_json_resource
        # dump_json_resource(normalized_users, 'normalized-users.json')

        assert normalized_users == get_json_resource('normalized-users.json')

    def test_normalize_user_should_not_mutate(self):
        user = get_json_resource('api-users-v1.json')[0]

        original_arg = deepcopy(user)

        nuser = normalize_user(user)

        assert user == original_arg

    def test_normalize_tweets_payload_v2(self):
        with pytest.raises(TypeError):
            normalize_tweets_payload_v2('test')

        tz = timezone('Europe/Paris')

        payloads = [
            get_json_resource('payload-v2.json'),
            get_json_resource('payload-v2-geo.json'),
            get_json_resource('payload-v2-tweet-retweet.json')
        ]

        ntweets = []

        for payload in payloads:
            ntweets.extend(normalize_tweets_payload_v2(payload, locale=tz, collection_source='test'))

        # print()
        # for t in ntweets:
        #     print()
        #     for k, v in sorted(t.items()):
        #         print('%s: %r' % (k, v))
        # print()

        # from test.utils import dump_json_resource
        # dump_json_resource(ntweets, 'normalized-tweets-v2.json')

        test_data = get_json_resource('normalized-tweets-v2.json')

        for t1, t2 in zip(ntweets, test_data):
            assert 'collection_time' in t1 and isinstance(t1['collection_time'], str)
            compare_tweets(t2['id'], t1, t2)

        # Testing extracting referenced tweets
        all_ntweets = []

        for payload in payloads:
            batch = normalize_tweets_payload_v2(payload, extract_referenced_tweets=True, collection_source='test')
            assert sorted(set(t['id'] for t in batch)) == sorted(t['id'] for t in batch)
            all_ntweets.extend(batch)

        all_ntweets = sorted_uniq(all_ntweets, key=itemgetter('id'))

        assert len(ntweets) < len(all_ntweets)

        # from test.utils import dump_json_resource
        # dump_json_resource(all_ntweets, 'normalized-tweets-v2-all.json')

        test_data = get_json_resource('normalized-tweets-v2-all.json')

        for t1, t2 in zip(all_ntweets, test_data):
            assert 'collection_time' in t1 and isinstance(t1['collection_time'], str)
            compare_tweets(t2['id'], t1, t2)
