# =============================================================================
# Twitwi Utilities
# =============================================================================
#
# Miscellaneous utility functions.
#
import re
from functools import partial
from datetime import datetime
from pytz import timezone
from ural import normalize_url
from html import unescape

from twitwi.constants import (
    TWEET_DATETIME_FORMAT,
    FORMATTED_TWEET_DATETIME_FORMAT,
    CANONICAL_URL_KWARGS
)

UTC_TIMEZONE = timezone('UTC')
CLEAN_RT_PATTERN = re.compile(r'^RT @\w+: ')


def get_dates(date_str, locale=None):
    parsed_datetime = datetime.strptime(date_str, TWEET_DATETIME_FORMAT)
    utc_datetime = parsed_datetime
    locale_datetime = parsed_datetime

    if locale:
        utc_datetime = UTC_TIMEZONE.localize(parsed_datetime)
        locale_datetime = utc_datetime.astimezone(locale)

    return (
        int(utc_datetime.timestamp()),
        datetime.strftime(locale_datetime, FORMATTED_TWEET_DATETIME_FORMAT)
    )


custom_normalize_url = partial(
    normalize_url,
    **CANONICAL_URL_KWARGS
)


def extract_items_from_text(text, char):
    splitter = re.compile(r'[^\w%s]+' % char)

    return sorted(
        set(
            r.lstrip(char).lower()
            for r in splitter.split(CLEAN_RT_PATTERN.sub('', text))
            if r.startswith(char)
        )
    )


def extract_hashtags_from_text(text):
    return extract_items_from_text(text, '#')


def extract_mentions_from_text(text):
    return extract_items_from_text(text, '@')


def resolve_entities(tweet, prefix):
    status_key = '%s_status' % prefix

    for ent in ['entities', 'extended_entities']:
        if ent not in tweet[status_key]:
            continue
        tweet[ent] = tweet.get(ent, {})
        for field in tweet[status_key][ent]:
            tweet[ent][field] = tweet[ent].get(field, [])
            if field in tweet[status_key][ent]:
                tweet[ent][field] += tweet[status_key][ent][field]


def get_bitrate(x):
    return x.get('bitrate', 0)


def nostr_field(f):
    return f.replace('_str', '')


META_FIELDS = [
    'in_reply_to_status_id_str',
    'in_reply_to_screen_name',
    'in_reply_to_user_id_str',
    'lang',
    'possibly_sensitive',
    'retweet_count',
    'favorite_count',
    'reply_count'
]

META_FIELD_TRANSLATIONS = {
    'in_reply_to_status_id_str': 'to_tweetid',
    'in_reply_to_screen_name': 'to_username',
    'in_reply_to_user_id_str': 'to_userid',
    'favorite_count': 'like_count'
}

USER_META_FIELDS = [
    'id_str',
    'screen_name',
    'name',
    'friends_count',
    'followers_count',
    'location',
    'verified',
    'description',
    'created_at'
]

PLACE_META_FIELDS = [
    'country_code',
    'full_name',
    'place_type'
]


def grab_extra_meta(source, result, locale=None):

    if source.get('coordinates'):
        result['coordinates'] = source['coordinates']['coordinates']
        result['lat'] = source['coordinates']['coordinates'][1]
        result['lng'] = source['coordinates']['coordinates'][0]
    else:

        # TODO: this is hardly optimal
        result['coordinates'] = None

    for meta in META_FIELDS:
        if meta in source:
            result[META_FIELD_TRANSLATIONS.get(meta, meta)] = source[meta]
        elif nostr_field(meta) in source:
            result[meta] = str(source[nostr_field(meta)])

    for meta in USER_META_FIELDS:
        key = 'user_%s' % meta.replace('_count', '')

        if key in source:
            result[nostr_field(key)] = source[key]
        elif nostr_field(key) in source:
            result[nostr_field(key)] = str(source[nostr_field(key)])
        elif 'user' in source and meta in source['user']:
            result[nostr_field(key)] = source['user'][meta]
        elif 'user' in source and nostr_field(meta) in source['user']:
            result[nostr_field(key)] = source['user'][nostr_field(meta)]

    if 'user' in source:
        result['user_tweets'] = source['user']['statuses_count']
        result['user_likes'] = source['user']['favourites_count']
        result['user_lists'] = source['user']['listed_count']
        result['user_image'] = source['user']['profile_image_url_https']

    if 'place' in source and source['place'] is not None:
        for meta in PLACE_META_FIELDS:
            if meta in source['place']:
                key = 'place_%s' % meta.replace('place_', '').replace('full_', '')
                result[key] = source['place'][meta]

        if 'bounding_box' in source['place'] \
                and source['place']['bounding_box'] is not None \
                and 'coordinates' in source['place']['bounding_box']:
            result['place_coordinates'] = source['place']['bounding_box']['coordinates'][0]

    # TODO: nested_get
    try:
        result['user_url'] = source['user']['entities']['url']['urls'][0]['expanded_url']
    except (KeyError, IndexError):
        try:
            result['user_url'] = source['user']['url']
        except KeyError:
            pass

    if 'user_created_at' in result:
        result['user_timestamp_utc'], result['user_created_at'] = get_dates(result['user_created_at'], locale)

    if source.get('source'):
        result['source_url'], result['source_name'] = source['source'].replace('<a href="', '').replace('</a>', '').split('" rel="nofollow">')

    return result


def normalize_tweet(tweet, locale=None, id_key='id', extract_referenced_tweets=False,
                    collection_source=None):
    """
    Function "normalizing" a tweet as returned by Twitter's API in order to
    cleanup and optimize some fields.

    Args:
        tweet (dict): Tweet json dict from Twitter API.
        locale (pytz.timezone, optional): Timezone for date conversions.
        id_key (str, optional): Name of the tweet id key.
            Defaults to `id`.
        extract_referenced_tweets (bool, optional): Whether to return only
            the original tweet or the full list of tweets found in the given
            tweet payload (including quoted and retweeted tweets). Defaults
            to `False`.
        collection_source (str, optional): string explaining how the tweet
            was collected. Defaults to `None`.

    Returns:
        (dict or list): Either a single tweet dict or a list of tweet dicts if
            `extract_referenced_tweets` was set to `True`.

    """

    results = []

    if 'extended_tweet' in tweet:
        for field in tweet['extended_tweet']:
            tweet[field] = tweet['extended_tweet'][field]

    text = tweet.get('full_text', tweet.get('text', ''))

    rti = None
    rtu = None
    rtuid = None
    rtime = None

    if 'retweeted_status' in tweet and tweet['retweeted_status']['id_str'] != tweet['id_str']:
        rti = tweet['retweeted_status']['id_str']
        rtu = tweet['retweeted_status']['user']['screen_name']
        rtuid = tweet['retweeted_status']['user']['id_str']

        nested = normalize_tweet(
            tweet['retweeted_status'],
            locale=locale,
            id_key=id_key,
            extract_referenced_tweets=True,
            collection_source='retweet'
        )

        rtweet = nested[-1]

        if extract_referenced_tweets:
            results.extend(nested)

        rtime = rtweet['timestamp_utc']
        text = 'RT @%s: %s' % (rtu, rtweet['text'])

        resolve_entities(tweet, 'retweeted')

    qti = None
    qtu = None
    qtuid = None
    qtime = None

    if 'quoted_status' in tweet and tweet['quoted_status']['id_str'] != tweet['id_str']:
        qti = tweet['quoted_status']['id_str']
        qtu = tweet['quoted_status']['user']['screen_name']
        qtuid = tweet['quoted_status']['user']['id_str']

        nested = normalize_tweet(
            tweet['quoted_status'],
            locale=locale,
            id_key=id_key,
            extract_referenced_tweets=True,
            collection_source='quote'
        )

        qtweet = nested[-1]

        if extract_referenced_tweets:
            results.extend(nested)

        if 'quoted_status_permalink' in tweet:
            qturl = tweet['quoted_status_permalink']['url']
        else:
            qturl = qtweet['url']
        qtime = qtweet['timestamp_utc']
        text = text.replace(qturl, u'« %s: %s — %s »' %
                            (qtu, qtweet['text'], qturl))

        resolve_entities(tweet, 'quoted')

    medids = set()
    media_urls = []
    media_files = []
    media_types = []

    links = set()
    hashtags = set()
    mentions = {}

    if 'entities' in tweet or 'extended_entities' in tweet:
        source_id = rti or qti or tweet['id_str']

        entities = tweet.get('extended_entities', tweet['entities']).get('media', [])
        entities += tweet['entities'].get('urls', [])

        for entity in entities:
            if 'expanded_url' in entity and 'url' in entity and entity['expanded_url']:
                try:
                    text = text.replace(entity['url'], entity['expanded_url'])
                except KeyError:
                    pass

            if 'media_url' in entity:
                if 'video_info' in entity:
                    med_url = max(entity['video_info']['variants'], key=get_bitrate)['url']
                else:
                    med_url = entity['media_url_https']

                med_name = med_url.rsplit('/', 1)[-1].split('?tag=', 1)[0]

                if med_name not in medids:
                    medids.add(med_name)
                    media_types.append(entity['type'])
                    media_urls.append(med_url.split('?tag=')[0])
                    media_files.append('%s_%s' % (source_id, med_name))
            else:
                normalized = custom_normalize_url(entity['expanded_url'])
                links.add(normalized)

        for hashtag in tweet['entities'].get('hashtags', []):
            hashtags.add(hashtag['text'].lower())

        for mention in tweet['entities'].get('user_mentions', []):
            mentions[mention['screen_name'].lower()] = mention['id_str']

    timestamp_utc, local_time = get_dates(tweet['created_at'], locale)
    text = unescape(text)

    if collection_source is None:
        collection_source = tweet.get('collection_source')

    prepared_tweet = {
        id_key: tweet['id_str'],
        'local_time': local_time,
        'timestamp_utc': timestamp_utc,
        'text': text,
        'url': 'https://twitter.com/%s/statuses/%s' % (tweet['user']['screen_name'], tweet['id_str']),
        'quoted_id': qti,
        'quoted_user': qtu,
        'quoted_user_id': qtuid,
        'quoted_timestamp_utc': qtime,
        'retweeted_id': rti,
        'retweeted_user': rtu,
        'retweeted_user_id': rtuid,
        'retweeted_timestamp_utc': rtime,
        'media_files': media_files,
        'media_types': media_types,
        'media_urls': media_urls,
        'links': sorted(links),
        'links_to_resolve': len(links) > 0,
        'hashtags': sorted(hashtags) if hashtags else extract_hashtags_from_text(text),
        'mentioned_ids': [mentions[m] for m in sorted(mentions.keys())],
        'mentioned_names': sorted(mentions.keys()) if mentions else extract_mentions_from_text(text),
        'collection_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
        'collected_via': [collection_source],
        'match_query': collection_source != 'thread' and collection_source != 'quote'
    }

    grab_extra_meta(tweet, prepared_tweet, locale)

    results.append(prepared_tweet)

    if not extract_referenced_tweets:
        return results[0]

    return results
