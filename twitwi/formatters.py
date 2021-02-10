# =============================================================================
# Twitwi Formatters
# =============================================================================
#
# Miscellaneous formatter functions transforming tweets from one format
# to the other.
#
from twitwi.constants import (
    TWEET_BOOLEAN_FIELDS,
    TWEET_PLURAL_FIELDS
)


def transform_tweet_into_csv_dict(tweet, tweet_id=None, plural_separator='|'):
    if tweet_id is not None:
        tweet['id'] = tweet_id

    tweet['links'] = tweet.get('proper_links', tweet.get('links', []))

    for plural_field in TWEET_PLURAL_FIELDS:
        tweet[plural_field] = plural_separator.join(tweet.get(plural_field, []))

    for boolean_field in TWEET_BOOLEAN_FIELDS:
        tweet[boolean_field] = int(tweet[boolean_field]) if boolean_field in tweet else ''
