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


def transform_tweet_into_csv_dict(tweet, normalize_id=False, has_proper_links=False,
                                  plural_separator='|'):
    if normalize_id:
        tweet['id'] = tweet['_id']

    if has_proper_links:
        tweet['links'] = tweet.get('proper_links', tweet.get('links', []))

    for plural_field in TWEET_PLURAL_FIELDS:
        tweet[plural_field] = plural_separator.join(tweet[plural_field])

    for boolean_field in TWEET_BOOLEAN_FIELDS:
        tweet[plural_field] = '1' if tweet.get(boolean_field, False) else ''
