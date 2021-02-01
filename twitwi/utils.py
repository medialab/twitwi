# =============================================================================
# Twitwi Utilities
# =============================================================================
#
# Miscellaneous utility functions.
#
from datetime import datetime
from pytz import timezone
from ural import normalize_url
from html import unescape
import re


from twitwi.constants import (
    TWEET_DATETIME_FORMAT,
    FORMATTED_TWEET_DATETIME_FORMAT,
    SHORT_FIELDNAMES
)

UTC_TIMEZONE = timezone('UTC')
re_clean_rt = re.compile(r"^RT @\w+: ")


def get_dates(date_str, locale=None):
    parsed_datetime = datetime.strptime(date_str, TWEET_DATETIME_FORMAT)
    utc_datetime = parsed_datetime
    locale_datetime = parsed_datetime

    if locale:
        utc_datetime = UTC_TIMEZONE.localize(parsed_datetime)
        locale_datetime = utc_datetime.astimezone(locale)

    return (
        utc_datetime.timestamp(),
        datetime.strftime(locale_datetime, FORMATTED_TWEET_DATETIME_FORMAT)
    )


def normalize(url):
    return normalize_url(url, strip_authentication=False, strip_trailing_slash=False, strip_protocol=False,
                         strip_irrelevant_subdomains=False, strip_fragment=False, normalize_amp=False,
                         fix_common_mistakes=False, infer_redirection=False, quoted=True)


def process_extract(text, car):
    return sorted(set([r.lstrip(car).lower() for r in re.split(r'[^\w%s]+' % car, re_clean_rt.sub('', text)) if r.startswith(car)]))


def nostr_field(f):
    return f.replace('_str', '')


def grab_extra_meta(source, result, locale=None):
    for meta in ["in_reply_to_status_id_str", "in_reply_to_screen_name", "in_reply_to_user_id_str", "lang", "coordinates", "possibly_sensitive", "retweet_count", "favorite_count", "reply_count"]:
        if meta in source:
            if meta == "coordinates" and source["coordinates"]:
                result["coordinates"] = source["coordinates"]["coordinates"]
                result["lat"] = source["coordinates"]["coordinates"][1]
                result["lng"] = source["coordinates"]["coordinates"][0]
            if meta in SHORT_FIELDNAMES:
                result[SHORT_FIELDNAMES[meta]] = source[meta]
            else:
                result[meta] = source[meta]
        elif nostr_field(meta) in source:
            result[meta] = str(source[nostr_field(meta)])
    for meta in ['id_str', 'screen_name', 'name', 'friends_count', 'followers_count', 'location', 'verified', 'description', 'created_at']:
        key = "user_%s" % meta.replace('_count', '')
        if key in source:
            result[nostr_field(key)] = source[key]
        elif nostr_field(key) in source:
            result[nostr_field(key)] = str(source[nostr_field(key)])
        elif 'user' in source and meta in source['user']:
            result[nostr_field(key)] = source['user'][meta]
        elif 'user' in source and nostr_field(meta) in source['user']:
            result[nostr_field(key)] = source['user'][nostr_field(meta)]
    if "user" in source:
        result["user_tweets"] = source["user"]["statuses_count"]
        result["user_likes"] = source["user"]["favourites_count"]
        result["user_lists"] = source["user"]["listed_count"]
        result["user_image"] = source["user"]["profile_image_url_https"]
    if "place" in source and source["place"] is not None:
        for meta in ['country_code', 'full_name', 'place_type']:
            if meta in source['place']:
                key = "place_%s" % meta.replace('place_', '').replace('full_', '')
                result[key] = source['place'][meta]
        if "bounding_box" in source["place"] and "coordinates" in source["place"]["bounding_box"]:
            result["place_coordinates"] = source["place"]["bounding_box"]["coordinates"][0]
    try:
        result['user_url'] = source['user']['entities']['url']['urls'][0]['expanded_url']
    except:
        try:
            result['user_url'] = source['user']['url']
        except:
            pass
    try:
        result['user_timestamp_utc'], result['user_created_at'] = get_dates(
            result["user_created_at"], locale)
    except:
        pass
    if "source" in source and source["source"]:
        split_source = source['source'].replace('<a href="', '').replace('</a>', '').split('" rel="nofollow">')
        result['source_url'] = split_source[0]
        result['source_name'] = split_source[1]
    return result


def prepare_tweet(tweet, locale=None, id_key='id'):
        results = []
        if "extended_tweet" in tweet:
            for field in tweet["extended_tweet"]:
                tweet[field] = tweet["extended_tweet"][field]
        text = tweet.get('full_text', tweet.get('text', ''))
        rti = None
        rtu = None
        rtuid = None
        rtime = None
        if "retweeted_status" in tweet and tweet['retweeted_status']['id_str'] != tweet['id_str']:
            rti = tweet['retweeted_status']['id_str']
            rtu = tweet['retweeted_status']['user']['screen_name']
            rtuid = tweet['retweeted_status']['user']['id_str']
            tweet['retweeted_status']["gazouilloire_source"] = "retweet"
            nested = prepare_tweet(tweet['retweeted_status'], locale=locale, id_key=id_key)
            rtweet = nested[-1]
            results.extend(nested)
            rtime = rtweet['timestamp_utc']
            text = "RT @%s: %s" % (rtu, rtweet['text'])
            for ent in ['entities', 'extended_entities']:
                if ent not in tweet['retweeted_status']:
                    continue
                tweet[ent] = tweet.get(ent, {})
                for field in tweet['retweeted_status'][ent]:
                    tweet[ent][field] = tweet[ent].get(field, [])
                    if field in tweet['retweeted_status'][ent]:
                        tweet[ent][field] += tweet['retweeted_status'][ent][field]
        qti = None
        qtu = None
        qtuid = None
        qtime = None
        if "quoted_status" in tweet and tweet['quoted_status']['id_str'] != tweet['id_str']:
            qti = tweet['quoted_status']['id_str']
            qtu = tweet['quoted_status']['user']['screen_name']
            qtuid = tweet['quoted_status']['user']['id_str']
            tweet['quoted_status']["gazouilloire_source"] = "quote"
            nested = prepare_tweet(tweet['quoted_status'], locale=locale, id_key=id_key)
            qtweet = nested[-1]
            results.extend(nested)
            if 'quoted_status_permalink' in tweet:
                qturl = tweet['quoted_status_permalink']['url']
            else:
                qturl = qtweet['url']
            qtime = qtweet['timestamp_utc']
            text = text.replace(qturl, u"« %s: %s — %s »" %
                                (qtu, qtweet['text'], qturl))
            for ent in ['entities', 'extended_entities']:
                if ent not in tweet['quoted_status']:
                    continue
                tweet[ent] = tweet.get(ent, {})
                for field in tweet['quoted_status'][ent]:
                    tweet[ent][field] = tweet[ent].get(field, [])
                    if field in tweet['quoted_status'][ent]:
                        tweet[ent][field] += tweet['quoted_status'][ent][field]
        medids = set()
        media_urls = []
        media_files = []
        media_types = []
        links = set()
        hashtags = set()
        mentions = {}
        if 'entities' in tweet or 'extended_entities' in tweet:
            source_id = rti or qti or tweet['id_str']
            for entity in tweet.get('extended_entities', tweet['entities']).get('media', []) + tweet['entities'].get(
                    'urls', []):
                if 'expanded_url' in entity and 'url' in entity and entity['expanded_url']:
                    try:
                        text = text.replace(entity['url'], entity['expanded_url'])
                    except:
                        pass
                if "media_url" in entity:
                    if "video_info" in entity:
                        med_url = sorted(entity["video_info"]["variants"], key=lambda x: x.get(
                            "bitrate", 0))[-1]["url"]
                    else:
                        med_url = entity["media_url_https"]
                    med_name = med_url.split('/')[-1].split("?tag=")[0]
                    if med_name not in medids:
                        medids.add(med_name)
                        media_types.append(entity["type"])
                        media_urls.append(med_url.split("?tag=")[0])
                        media_files.append("%s_%s" % (source_id, med_name))
                else:
                    normalized = normalize(entity["expanded_url"])
                    links.add(normalized)
            for hashtag in tweet['entities'].get('hashtags', []):
                hashtags.add(hashtag['text'].lower())
            for mention in tweet['entities'].get('user_mentions', []):
                mentions[mention['screen_name'].lower()] = mention['id_str']
        timestamp_utc, local_time = get_dates(tweet["created_at"], locale)
        text = unescape(text)
        tw = {
            id_key: tweet['id_str'],
            'local_time': local_time,
            'timestamp_utc': timestamp_utc,
            'text': text,
            'url': "https://twitter.com/%s/statuses/%s" % (tweet['user']['screen_name'], tweet['id_str']),
            'quoted_id': qti,
            'quoted_user': qtu,
            'quoted_user_id': qtuid,
            'quoted_timestamp_utc': qtime,
            'retweeted_id': rti,
            'retweeted_user': rtu,
            'retweeted_user_id': rtuid,
            'retweeted_timestamp_utc': rtime,
            "media_files": media_files,
            'media_types': media_types,
            'media_urls': media_urls,
            'links': sorted(links),
            'links_to_resolve': len(links) > 0,
            'hashtags': sorted(hashtags) if hashtags else process_extract(text, "#"),
            'mentioned_ids': [mentions[m] for m in sorted(mentions.keys())],
            'mentioned_names': sorted(mentions.keys()) if mentions else process_extract(text, "@"),
            'collection_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'collected_via': [tweet["gazouilloire_source"]],
            'match_query': tweet["gazouilloire_source"] != "thread" and tweet["gazouilloire_source"] != "quote"
        }

        tw = grab_extra_meta(tweet, tw, locale)
        results.append(tw)
        return results
