# =============================================================================
# Twitwi Formatters
# =============================================================================
#
# Miscellaneous formatter functions transforming tweets from one format
# to the other.
#
from twitwi.constants import (
    TWEET_FIELDS,
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


def format_tweet_field_for_csv(field, tweet, tweet_id=None, plural_separator='|'):

    if field == 'id' and tweet_id is not None:
        return tweet_id

    # NOTE: this is hardly the most performant way to proceed by I am lazy...
    if field in TWEET_PLURAL_FIELDS:
        v = tweet.get(field, [])

        if field == 'links':
            v = tweet.get('proper_links', v)

        return plural_separator.join(v)

    if field in TWEET_BOOLEAN_FIELDS:
        return int(tweet[field]) if field in tweet else ''

    return tweet.get(field, '')


def format_tweet_as_csv_row(tweet, tweet_id=None, plural_separator='|'):
    return [
        format_tweet_field_for_csv(
            field,
            tweet,
            tweet_id=tweet_id,
            plural_separator=plural_separator
        )
        for field in TWEET_FIELDS
    ]
