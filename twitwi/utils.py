# =============================================================================
# Twitwi Utilities
# =============================================================================
#
# Miscellaneous utility functions.
#
import re
from copy import deepcopy
from functools import partial
from datetime import datetime
from pytz import timezone
from ural import normalize_url
from html import unescape

from twitwi.constants import (
    TWEET_DATETIME_FORMAT,
    FORMATTED_TWEET_DATETIME_FORMAT,
    TWEET_DATETIME_FORMAT_V2,
    CANONICAL_URL_KWARGS
)

UTC_TIMEZONE = timezone('UTC')
CLEAN_RT_PATTERN = re.compile(r'^RT @\w+: ')


def get_dates(date_str, locale=None, v2=False):
    parsed_datetime = datetime.strptime(date_str, TWEET_DATETIME_FORMAT_V2 if v2 else TWEET_DATETIME_FORMAT)
    utc_datetime = parsed_datetime
    locale_datetime = parsed_datetime

    if locale:
        utc_datetime = UTC_TIMEZONE.localize(parsed_datetime)
        locale_datetime = utc_datetime.astimezone(locale)

    return (
        int(utc_datetime.timestamp()),
        datetime.strftime(locale_datetime, FORMATTED_TWEET_DATETIME_FORMAT)
    )


def get_collection_time():
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')


def format_rt_text(user, text):
    return 'RT @%s: %s' % (user, text)


def format_qt_text(user, text, quoted_text, url):
    quote = '« %s: %s — %s »' % (user, quoted_text, url)

    return text.replace(url, quote)


def format_tweet_url(screen_name, tweet_id):
    return 'https://twitter.com/%s/statuses/%s' % (screen_name, tweet_id)


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
    target = tweet[status_key]

    for ent in ['entities', 'extended_entities']:
        if ent not in target:
            continue
        tweet[ent] = tweet.get(ent, {})
        for field in target[ent]:
            tweet[ent][field] = tweet[ent].get(field, [])
            if field in target[ent]:
                tweet[ent][field] += target[ent][field]


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


def normalize_tweet(tweet, locale=None, extract_referenced_tweets=False,
                    collection_source=None, pure=True):
    """
    Function "normalizing" a tweet as returned by Twitter's API in order to
    cleanup and optimize some fields.

    Note that this function mutates the argument to work.

    Args:
        tweet (dict): Tweet json dict from Twitter API.
        locale (pytz.timezone, optional): Timezone for date conversions.
        extract_referenced_tweets (bool, optional): Whether to return only
            the original tweet or the full list of tweets found in the given
            tweet payload (including quoted and retweeted tweets). Defaults
            to `False`.
        collection_source (str, optional): string explaining how the tweet
            was collected. Defaults to `None`.
        pure (bool, optional): whether to allow the function to mutate its
            original argument. Default to `True`.

    Returns:
        (dict or list): Either a single tweet dict or a list of tweet dicts if
            `extract_referenced_tweets` was set to `True`.

    """

    if pure:
        tweet = deepcopy(tweet)

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
            extract_referenced_tweets=True,
            collection_source='retweet',
            pure=False
        )

        rtweet = nested[-1]

        if extract_referenced_tweets:
            results.extend(nested)

        rtime = rtweet['timestamp_utc']
        text = format_rt_text(rtu, rtweet['text'])

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
            extract_referenced_tweets=True,
            collection_source='quote',
            pure=False
        )

        qtweet = nested[-1]

        if extract_referenced_tweets:
            results.extend(nested)

        if 'quoted_status_permalink' in tweet:
            qturl = tweet['quoted_status_permalink']['url']
        else:
            qturl = qtweet['url']
        qtime = qtweet['timestamp_utc']
        text = format_qt_text(qtu, text, qtweet['text'], qturl)

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

    normalized_tweet = {
        'id': tweet['id_str'],
        'local_time': local_time,
        'timestamp_utc': timestamp_utc,
        'text': text,
        'url': format_tweet_url(tweet['user']['screen_name'], tweet['id_str']),
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
        'collection_time': get_collection_time(),
        'match_query': collection_source != 'thread' and collection_source != 'quote'
    }

    if collection_source is not None:
        normalized_tweet['collected_via'] = [collection_source]

    grab_extra_meta(tweet, normalized_tweet, locale)

    results.append(normalized_tweet)

    if not extract_referenced_tweets:
        return results[0]

    return results


def resolve_user_entities(user):
    if 'entities' in user:
        for k in user['entities']:
            if 'urls' in user['entities'][k]:
                for url in user['entities'][k]['urls']:
                    if not url['expanded_url']:
                        continue
                    if k in user:
                        user[k] = user[k].replace(url['url'], url['expanded_url'])


def normalize_user(user, locale=None, pure=True):
    """
    Function "normalizing" a user as returned by Twitter's API in order to
    cleanup and optimize some fields.

    Note that this function mutates the argument to work.

    Args:
        user (dict): Twitter user json dict from Twitter API.
        locale (pytz.timezone, optional): Timezone for date conversions.
        pure (bool, optional): whether to allow the function to mutate its
            original argument. Default to `True`.

    Returns:
        dict: The normalized user.

    """

    if pure:
        user = deepcopy(user)

    resolve_user_entities(user)

    timestamp_utc, local_time = get_dates(user['created_at'], locale)

    normalized_user = {
        'id': user['id_str'],
        'screen_name': user['screen_name'],
        'name': user['name'],
        'description': user['description'],
        'url': user['url'],
        'timestamp_utc': timestamp_utc,
        'local_time': local_time,
        'location': user.get('location'),
        'verified': user.get('verified'),
        'protected': user.get('protected'),
        'tweets': user['statuses_count'],
        'followers': user['followers_count'],
        'friends': user['friends_count'],
        'likes': user['favourites_count'],
        'lists': user['listed_count'],
        'image': user.get('profile_image_url_https'),
        'default_profile': user.get('default_profile'),
        'default_profile_image': user.get('default_profile_image'),
        'witheld_in_countries': user.get('witheld_in_countries', []),
        'witheld_scope': user.get('witheld_scope')
    }

    return normalized_user

# normalized_tweet = {
#     'id': tweet['id_str'],
#     'local_time': local_time,
#     'timestamp_utc': timestamp_utc,
#     'text': text,
#     'url': 'https://twitter.com/%s/statuses/%s' % (tweet['user']['screen_name'], tweet['id_str']),
#     'quoted_id': qti,
#     'quoted_user': qtu,
#     'quoted_user_id': qtuid,
#     'quoted_timestamp_utc': qtime,
#     'retweeted_id': rti,
#     'retweeted_user': rtu,
#     'retweeted_user_id': rtuid,
#     'retweeted_timestamp_utc': rtime,
#     'media_files': media_files,
#     'media_types': media_types,
#     'media_urls': media_urls,
#     'links': sorted(links),
#     'links_to_resolve': len(links) > 0,
#     'hashtags': sorted(hashtags) if hashtags else extract_hashtags_from_text(text),
#     'mentioned_ids': [mentions[m] for m in sorted(mentions.keys())],
#     'mentioned_names': sorted(mentions.keys()) if mentions else extract_mentions_from_text(text),
#     'collection_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
#     'match_query': collection_source != 'thread' and collection_source != 'quote'
# }


def includes_index(payload, key):
    return {item['id']: item for item in payload['includes'][key]}


def normalize_tweet_v2(tweet, user, locale=None):
    local_time, timestamp_utc = get_dates(tweet['created_at'], locale=locale, v2=True)

    entities = tweet.get('entities', {})

    hashtags = set()

    for hashtag in entities.get('hashtags', []):
        hashtags.add(hashtag['tag'])

    normalized_tweet = {
        'id': tweet['id'],
        'local_time': local_time,
        'timestamp_utc': timestamp_utc,
        'text': None,
        'url': format_tweet_url(user['username'], tweet['id']),
        'hashtags': sorted(hashtags),
        'collection_time': get_collection_time()
    }

    return normalized_tweet


def normalize_tweets_payload_v2(payload, locale=None, extract_referenced_tweets=False):
    users = includes_index(payload, 'users')
    refs = includes_index(payload, 'tweets')

    output = []

    for item in payload['data']:
        normalized_tweet = normalize_tweet_v2(item, users[item['author_id']], locale=locale)
        output.append(normalized_tweet)

    return output
