# =============================================================================
# Twitwi Normalizers
# =============================================================================
#
# Function used to "normalize" tweets from various sources (v1 API, v2 API,
# public scraped API etc.) in order to produce homogeneous and easily
# analysable data.
#
import re
from copy import deepcopy
from datetime import datetime
from html import unescape

from twitwi.utils import (
    get_dates,
    custom_normalize_url,
    validate_payload_v2,
    custom_get_normalized_hostname
)

CLEAN_RT_PATTERN = re.compile(r'^RT @\w+: ')


def get_collection_time():
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')


def format_rt_text(user, text):
    return 'RT @%s: %s' % (user, text)


def format_qt_text(user, text, quoted_text, url):
    clean_url = re.sub(r'(\?s=\d+|/(video|photo)/\d+)+', '', url.lower())
    quote = '« %s: %s — %s »' % (user, quoted_text, clean_url)
    text_lc = text.lower()
    if quote.lower() in text_lc:
        return text
    url_lc = url.lower()
    url_pos = text_lc.find(url_lc)
    if url_pos != -1:
        url_len = len(url)
        return ("%s%s%s" % (text[:url_pos], quote, text[url_pos + url_len:])).strip()
    return "%s %s" % (text, quote)


def format_tweet_url(screen_name, tweet_id):
    return 'https://twitter.com/%s/status/%s' % (screen_name, tweet_id)


def extract_media_name_from_url(media_url):
    return media_url.rsplit('/', 1)[-1].split('?tag=', 1)[0]


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

    # impression_count when scraping
    if 'ext_views' in source:
        result['impression_count'] = source['ext_views'].get('count')

    for meta in USER_META_FIELDS:
        key = 'user_%s' % meta.replace('_count', '')
        if key in source:
            result[key] = source[key]
        elif 'user' in source and meta in source['user']:
            result[key] = source['user'][meta] if source['user'][meta] != "" else None

    if 'user' in source:
        result['user_id'] = source['user']['id_str']
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
    qti = None
    qturl = None
    qtu = None
    qtuid = None
    qtime = None

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

        resolve_entities(tweet, 'retweeted')

    elif 'quoted_status' in tweet and tweet['quoted_status']['id_str'] != tweet['id_str']:
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

        if "quoted_status_permalink" in tweet:
            qturl = tweet['quoted_status_permalink']['expanded']
        else:
            qturl = qtweet['url']
        qtime = qtweet['timestamp_utc']

        resolve_entities(tweet, 'quoted')

    medids = set()
    media_urls = []
    media_files = []
    media_types = []
    media_alt_texts = []

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

                med_name = extract_media_name_from_url(med_url)

                if med_name not in medids:
                    medids.add(med_name)
                    media_types.append(entity['type'])
                    media_urls.append(med_url.split('?tag=')[0])
                    media_files.append('%s_%s' % (source_id, med_name))
                    media_alt_texts.append(entity.get("ext_alt_text") or '')
            else:
                normalized = custom_normalize_url(entity['expanded_url'])
                links.add(normalized)

        for hashtag in tweet['entities'].get('hashtags', []):
            hashtags.add(hashtag['text'].lower())

        for mention in tweet['entities'].get('user_mentions', []):
            mentions[mention['screen_name'].lower()] = mention['id_str']

    if rtu:
        text = format_rt_text(rtu, rtweet['text'])
        if rtweet["quoted_id"]:
            qturl = format_tweet_url(rtweet["quoted_user"], rtweet["quoted_id"])

    elif qtu:
        text = format_qt_text(qtu, text, qtweet['text'], qturl)

    if qturl:
        qturl_lc = custom_normalize_url(qturl).lower()
        for link in list(links):
            if link.lower() == qturl_lc:
                links.remove(link)

    timestamp_utc, local_time = get_dates(tweet['created_at'], locale)
    text = unescape(text)

    if collection_source is None:
        collection_source = tweet.get('collection_source')
    links = sorted(links)
    domains = [custom_get_normalized_hostname(link, normalize_amp=False, infer_redirection=False)
               for link in links]
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
        'media_alt_texts': media_alt_texts,
        'links': links,
        'links_to_resolve': len(links) > 0,
        'domains': domains,
        'hashtags': sorted(hashtags) if hashtags else extract_hashtags_from_text(text),
        'mentioned_ids': [mentions[m] for m in sorted(mentions.keys())],
        'mentioned_names': sorted(mentions.keys()) if mentions else extract_mentions_from_text(text),
        'collection_time': get_collection_time(),
        'match_query': collection_source != 'thread' and collection_source != 'quote'
    }

    if collection_source is not None:
        normalized_tweet['collected_via'] = [collection_source]

    grab_extra_meta(tweet, normalized_tweet, locale)

    if rtu and not normalized_tweet["retweet_count"]:
        normalized_tweet["retweet_count"] = rtweet["retweet_count"]

    results.append(normalized_tweet)

    if not extract_referenced_tweets:
        return results[0]

    return results


def resolve_user_entities(user):
    if 'entities' in user:
        for k in user['entities']:
            if 'urls' in user['entities'][k]:
                for url in user['entities'][k]['urls']:
                    if not url.get('expanded_url'):
                        continue
                    if k in user:
                        user[k] = user[k].replace(url['url'], url['expanded_url'])


def normalize_user(user, locale=None, pure=True, v2=False):
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

    timestamp_utc, local_time = get_dates(user['created_at'], locale, v2)

    if v2 and 'withheld' in user:
        withheld = user['withheld']
        withheld_in_countries = withheld.get('country_codes', [])
        withheld_scope = withheld.get('withheld_scope', '')
    else:
        withheld_in_countries = []
        withheld_scope = ''

    normalized_user = {
        'id': user['id_str'] if not v2 else user['id'],
        'screen_name': user['screen_name'] if not v2 else user['username'],
        'name': user['name'],
        'description': user['description'] if user["description"] else None,
        'url': user.get('url'),
        'timestamp_utc': timestamp_utc,
        'local_time': local_time,
        'location': user.get('location'),
        'verified': user.get('verified'),
        'protected': user.get('protected'),
        'tweets': user['statuses_count'] if not v2 else user['public_metrics']['tweet_count'],
        'followers': user['followers_count'] if not v2 else user['public_metrics']['followers_count'],
        'friends': user['friends_count'] if not v2 else user['public_metrics']['following_count'],
        'likes': user['favourites_count'] if not v2 else None,
        'lists': user['listed_count'] if not v2 else user['public_metrics']['listed_count'],
        'image': user.get('profile_image_url_https') if not v2 else user.get('profile_image_url'),
        'default_profile': user.get('default_profile', False),
        'default_profile_image': user.get('default_profile_image', False),
        'witheld_in_countries': user.get('witheld_in_countries', []) if not v2 else withheld_in_countries,
        'witheld_scope': user.get('witheld_scope') if not v2 else withheld_scope
    }

    return normalized_user


def includes_index(payload, key, index_key='id'):
    return {item[index_key]: item for item in payload['includes'].get(key, [])}


def get_best_url(item):
    if 'unwound_url' in item:
        return item['unwound_url']

    if 'expanded_url' in item:
        return item['expanded_url']

    return None


def normalize_tweet_v2(tweet, *, users_by_screen_name, places_by_id, tweets_by_id,
                       users_by_id, media_by_key, locale=None, collection_source=None,
                       extract_referenced_tweets=False):
    timestamp_utc, local_time = get_dates(tweet['created_at'], locale=locale, v2=True)

    user = users_by_id[tweet['author_id']]
    user_timestamp_utc, user_created_at = get_dates(user['created_at'], locale=locale, v2=True)
    user_entities = user.get('entities', {})

    entities = tweet.get('entities', {})
    referenced_tweets = tweet.get('referenced_tweets', [])

    hashtags = set()

    for hashtag in entities.get('hashtags', []):
        hashtags.add(hashtag['tag'])

    mentions = {}

    for mention in entities.get('mentions', []):
        if 'id' in mention:
            mentions[mention['username']] = mention['id']
        else:
            mentions[mention['username']] = users_by_screen_name[mention['username']]['id']

    place_info = {}

    if 'geo' in tweet:
        geo_data = tweet['geo']

        if 'coordinates' in geo_data:
            point = geo_data['coordinates']

            if point['type'] == 'Point':
                lng, lat = point['coordinates']
                place_info['lng'] = lng
                place_info['lat'] = lat

        if 'place_id' in geo_data:
            place_data = places_by_id.get(geo_data['place_id'], {})

            if 'country_code' in place_data:
                place_info['place_country_code'] = place_data['country_code']

            if 'full_name' in place_data:
                place_info['place_name'] = place_data['full_name']

            if 'place_type' in place_data:
                place_info['place_type'] = place_data['place_type']

            if 'geo' in place_data and 'bbox' in place_data['geo']:
                place_info['place_coordinates'] = place_data['geo']['bbox']

    # Text
    text = tweet['text']

    # References
    refs = {t['type']: t['id'] for t in referenced_tweets}

    # Reply
    reply_info = {}

    if 'replied_to' in refs:
        reply = tweets_by_id.get(refs['replied_to'], {})
        if 'author_id' in reply:
            reply_info['to_username'] = users_by_id[reply['author_id']]['username']
        else:
            reply_info['to_username'] = ''
        reply_info['to_userid'] = reply.get('author_id', '')
        reply_info['to_tweetid'] = reply.get('id', '')

    # Retweet
    retweet_info = {}
    normalized_retweet = None

    if 'retweeted' in refs:
        retweet_info['retweeted_id'] = refs['retweeted']

        if refs['retweeted'] in tweets_by_id:
            retweet = tweets_by_id[refs['retweeted']]
            normalized_retweet = normalize_tweet_v2(
                retweet,
                users_by_screen_name=users_by_screen_name,
                places_by_id=places_by_id,
                tweets_by_id=tweets_by_id,
                users_by_id=users_by_id,
                media_by_key=media_by_key,
                locale=locale,
                collection_source='retweet'
            )

            retweet_info['retweeted_user'] = normalized_retweet['user_screen_name']
            retweet_info['retweeted_user_id'] = normalized_retweet['user_id']
            retweet_info['retweeted_timestamp_utc'] = normalized_retweet['timestamp_utc']

    # Quoted
    quote_info = {}
    normalized_quote = None

    if 'quoted' in refs:
        quote_info['quoted_id'] = refs['quoted']

        if refs['quoted'] in tweets_by_id:
            quote = tweets_by_id[refs['quoted']]
            normalized_quote = normalize_tweet_v2(
                quote,
                users_by_screen_name=users_by_screen_name,
                places_by_id=places_by_id,
                tweets_by_id=tweets_by_id,
                users_by_id=users_by_id,
                media_by_key=media_by_key,
                locale=locale,
                collection_source='quote'
            )

            quote_info['quoted_user'] = normalized_quote['user_screen_name']
            quote_info['quoted_user_id'] = normalized_quote['user_id']
            quote_info['quoted_timestamp_utc'] = normalized_quote['timestamp_utc']

    # Replace urls in text
    links = set()

    for url_data in entities.get('urls', []):
        replacement_url = get_best_url(url_data)

        if replacement_url:
            text = text.replace(url_data['url'], replacement_url)

        if not replacement_url:
            replacement_url = url_data['url']

        links.add(custom_normalize_url(replacement_url))

    if normalized_retweet:
        text = format_rt_text(
            normalized_retweet['user_screen_name'],
            normalized_retweet['text']
        )

    if normalized_quote:
        text = format_qt_text(
            normalized_quote['user_screen_name'],
            text,
            normalized_quote['text'],
            normalized_quote['url']
        )

    # Metrics
    is_retweet = 'retweeted' in refs
    public_metrics = tweet['public_metrics']
    user_public_metrics = user['public_metrics']

    user_url = user.get('url')

    if 'url' in user_entities and 'urls' in user_entities['url']:
        user_url_entity = user_entities['url']['urls'][0]
        user_url = get_best_url(user_url_entity) or user_url

    medias = []

    if 'attachments' in tweet and 'media_keys' in tweet['attachments']:
        source_id = refs.get('retweeted_id', tweet['id'])

        for media_key in tweet['attachments']['media_keys']:
            if media_key in media_by_key:
                media_data = media_by_key[media_key]

                medias.append((
                    media_data.get('url', ''),
                    '%s_%s' % (source_id, extract_media_name_from_url(media_data.get('url', ''))),
                    media_data['type']
                ))

    if collection_source is None:
        collection_source = tweet.get('collection_source')

    sorted_mentions = sorted(mentions.keys())

    normalized_tweet = {
        'id': tweet['id'],
        'local_time': local_time,
        'timestamp_utc': timestamp_utc,
        'text': unescape(text),
        'url': format_tweet_url(user['username'], tweet['id']),
        'hashtags': sorted(hashtags),
        'mentioned_names': sorted_mentions,
        'mentioned_ids': [mentions[k] for k in sorted_mentions],
        'collection_time': get_collection_time(),
        'user_id': user['id'],
        'user_screen_name': user['username'],
        'user_name': user['name'],
        'user_image': user['profile_image_url'],
        'user_url': user_url or None,
        'user_location': user.get("location"),
        'user_verified': user['verified'],
        'user_description': user['description'] if user["description"] else None,
        'user_tweets': user_public_metrics['tweet_count'],
        'user_followers': user_public_metrics['followers_count'],
        'user_friends': user_public_metrics['following_count'],
        'user_lists': user_public_metrics['listed_count'],
        'user_created_at': user_created_at,
        'user_timestamp_utc': user_timestamp_utc,
        'possibly_sensitive': tweet['possibly_sensitive'],
        'like_count': public_metrics['like_count'] if not is_retweet else 0,
        'retweet_count': public_metrics['retweet_count'] if not is_retweet else 0,
        'quote_count': public_metrics['quote_count'] if not is_retweet else 0,
        'reply_count': public_metrics['reply_count'] if not is_retweet else 0,
        'impression_count': public_metrics.get('impression_count'),
        'lang': tweet['lang'],
        'source_name': tweet.get('source'),
        'links': sorted(links),
        'media_urls': [m[0] for m in medias],
        'media_files': [m[1] for m in medias],
        'media_types': [m[2] for m in medias],
        'match_query': collection_source != 'thread' and collection_source != 'quote',
        **place_info,
        **reply_info,
        **retweet_info,
        **quote_info
    }

    if collection_source is not None:
        normalized_tweet['collected_via'] = [collection_source]

    if extract_referenced_tweets:
        normalized_tweets = [normalized_tweet]

        if normalized_retweet is not None:
            normalized_tweets.append(normalized_retweet)

        if normalized_quote is not None:
            normalized_tweets.append(normalized_quote)

        return normalized_tweets

    return normalized_tweet


def normalize_tweets_payload_v2(payload, locale=None, extract_referenced_tweets=False,
                                collection_source=None):

    if not validate_payload_v2(payload):
        raise TypeError('given value is not a Twitter API v2 payload')

    if 'data' not in payload:
        return []

    users_by_screen_name = includes_index(payload, 'users', index_key='username')
    users_by_id = includes_index(payload, 'users')
    places_by_id = includes_index(payload, 'places')
    tweets_by_id = includes_index(payload, 'tweets')
    media_by_key = includes_index(payload, 'media', index_key='media_key')

    output = []
    already_seen = {}

    for item in payload['data']:
        normalized_tweets = normalize_tweet_v2(
            item,
            users_by_id=users_by_id,
            users_by_screen_name=users_by_screen_name,
            places_by_id=places_by_id,
            tweets_by_id=tweets_by_id,
            media_by_key=media_by_key,
            locale=locale,
            collection_source=collection_source,
            extract_referenced_tweets=True
        )

        if extract_referenced_tweets:
            for normalized_tweet in normalized_tweets:
                k = int(normalized_tweet['id'])
                earlier_normalized_tweet = already_seen.get(k)

                if earlier_normalized_tweet is not None:
                    if 'collected_via' in normalized_tweet:
                        new_collection_source = normalized_tweet['collected_via'][0]

                        if 'collected_via' not in earlier_normalized_tweet:
                            earlier_normalized_tweet['collected_via'] = [new_collection_source]
                        else:
                            if new_collection_source not in earlier_normalized_tweet['collected_via']:
                                earlier_normalized_tweet['collected_via'].append(new_collection_source)

                    continue

                already_seen[k] = normalized_tweet
                output.append(normalized_tweet)
        else:
            assert len(normalized_tweets)
            output.append(normalized_tweets[0])

    return output
