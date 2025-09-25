[![Build Status](https://github.com/medialab/twitwi/workflows/Tests/badge.svg)](https://github.com/medialab/twitwi/actions)

# Twitwi

A collection of Twitter & Bluesky related helper functions for Python intended to preprocess JSON payloads from the platforms' APIs and return "normalized" flat versions in order to cleanup and optimize some fields before storing them into consistent tabular formats.

A description of the "normalized" fields [for Twitter is available here](twitwi/constants.py) and [for Bluesky there](twitwi/bluesky/types.py).

It also provides a few convenient tools to anonymize tweets data, convert it into other formats, or extract datetime/timestamp from Twitter IDs (without querying it to Twitter).

## Installation

You can install `twitwi` with pip with the following command:

```
pip install twitwi
```

## Requirements

- Python 3.8 +
- [pytz](https://pypi.org/project/pytz/) (for timezones handling)
- [ural](https://github.com/medialab/ural?tab=readme-ov-file#ural) (for urls cleaning)

## Usage

**Bluesky (within `twitwi.bluesky`)**

*Normalization functions*

* [normalize_profile](#normalize_profile)
* [normalize_partial_profile](#normalize_partial_profile)
* [normalize_post](#normalize_post)

*Formatting functions*

* [transform_profile_into_csv_dict](#transform_profile_into_csv_dict)
* [transform_partial_profile_into_csv_dict](#transform_partial_profile_into_csv_dict)
* [transform_post_into_csv_dict](#transform_post_into_csv_dict)
* [format_profile_as_csv_row](#format_profile_as_csv_row)
* [format_partial_profile_as_csv_row](#format_partial_profile_as_csv_row)
* [format_post_as_csv_row](#format_post_as_csv_row)

*Useful constants (under `twitwi.bluesky.constants`)*

* [PROFILE_FIELDS](#profile_fields)
* [PARTIAL_PROFILE_FIELDS](#partial_profile_fields)
* [POST_FIELDS](#post_fields)

*Examples*

```python

# Working with Blueksy posts payloads coming directly from the API, either from clasical payloads,
# for instance via the routes app.bsky.feed.getPosts https://docs.bsky.app/docs/api/app-bsky-feed-get-posts
# or app.bsky.feed.searchPosts https://docs.bsky.app/docs/api/app-bsky-feed-search-posts
# or from feeds payloads, such as the route app.bsky.feed.getAuthorFeed https://docs.bsky.app/docs/api/app-bsky-feed-get-author-feed

from twitwi.bluesky import normalize_post

normalized_posts = []
for post_data in posts_payload_from_API:
    normalized_posts.append(normalize_post(post_data))

    # Or to convert found datetimes into a local chosen timezone
    from pytz import timezone
    paris_tz = timezone('Europe/Paris')
    normalized_posts.append(normalize_post(post_data, locale=paris_tz))

    # Or to also produce full metadata for other posts embedded such as quotes or posts answered to:
    normalized_posts += normalize_post(post_data, extract_referenced_posts=True)    # Returns a list of dicts

# Then, saving normalized profiles into a CSV using DictWriter:

import csv
from twitwi.bluesky.constants import POST_FIELDS
from twitwi.bluesky import transform_post_into_csv_dict

with open("normalized_bluesky_posts.csv", "w") as f:
    w = csv.DictWriter(f, fieldnames=POST_FIELDS)
    w.writeheader()
    for p in normalized_posts:
        transform_post_into_csv_dict(p)  # The function returns nothing, p has been mutated
        w.writerow(p)

# Or using the basic CSV writer:

from twitwi.bluesky import format_post_as_csv_row

with open("normalized_bluesky_posts.csv", "w") as f:
    w = csv.writer(f)
    w.writerow(POST_FIELDS)
    for p in normalized_posts:
        w.writerow(format_post_as_csv_row(p))


# Similarily, working with Bluesky user profiles coming directly from the API
# for instance via the route app.bsky.actor.getProfiles https://docs.bsky.app/docs/api/app-bsky-actor-get-profiles

from twitwi.bluesky import normalize_profile

normalized_profiles = []
for profile_data in profiles_payload_from_API:
    normalized_profiles.append(normalize_profile(profile_data))

    # Or in the local timezone
    normalized_profiles.append(normalize_profile(profile_payload, locale=paris_tz))

# Then saving as a CSV with csv.writer or csv.DictWriter similarily:

from twitwi.bluesky.constants import PROFILE_FIELDS
from twitwi.bluesky import transform_profile_into_csv_dict, format_profile_as_csv_row

with open("normalized_bluesky_profiles.csv", "w") as f:
    w = csv.DictWriter(f, fieldnames=PROFILE_FIELDS)
    w.writeheader()
    for p in normalized_profiles:
        transform_profile_into_csv_dict(p)  # The function returns nothing, p has been mutated
        w.writerow(p)

with open("normalized_bluesky_profiles.csv", "w") as f:
    w = csv.writer(f)
    w.writerow(PROFILE_FIELDS)
    for p in normalized_profiles:
        w.writerow(format_profile_as_csv_row(p))
```


**Twitter (within `twitwi`)**

*Normalization functions*

* [normalize_user](#normalize_user)
* [normalize_tweet](#normalize_tweet)
* [normalize_tweets_payload_v2](#normalize_tweets_payload_v2)

*Formatting functions*

* [transform_user_into_csv_dict](#transform_user_into_csv_dict)
* [transform_tweet_into_csv_dict](#transform_tweet_into_csv_dict)
* [format_user_as_csv_row](#format_user_as_csv_row)
* [format_tweet_as_csv_row](#format_tweet_as_csv_row)
* [apply_tcat_format](#apply_tcat_format)

*Useful constants (under `twitwi.constants`)*

* [USER_FIELDS](#user_fields)
* [TWEET_FIELDS](#tweet_fields)

*Extra functions*

* [anonymize_normalized_tweet](#anonymize_normalized_tweet)
* [get_timestamp_from_id](#get_timestamp_from_id)
* [get_dates_from_id](#get_dates_from_id)


### normalize_profile

Function taking a nested dict describing a user profile from Bluesky's JSON payload (with the same format as retrieved from [`app.bsky.actor.getProfiles` HTTP endpoint](docs.bsky.app/docs/api/app-bsky-actor-get-profiles#responses)) and returning a flat "normalized" dict composed of all [PROFILE_FIELDS](#profile_fields) keys. Be careful not to confuse with the [normalize_partial_profile](#normalize_partial_profile) function which operate on a lighter version of the profile data, retrieved from [follower/follow profile payloads](https://docs.bsky.app/docs/api/app-bsky-graph-get-followers#responses) for example.

Will return datetimes as UTC but can take an optional second `locale` argument as a [`pytz`](https://pypi.org/project/pytz/) string timezone.

*Arguments*

* **data** *(dict)*: user profile data payload coming from Bluesky API.
* **locale** *(pytz.timezone as str, optional)*: timezone used to convert dates. If not given, will default to UTC.

### normalize_partial_profile

Function taking a nested dict describing a user profile from Bluesky's JSON payload (with the same format as retrieved from [`app.bsky.graph.getFollowers` HTTP endpoint](https://docs.bsky.app/docs/api/app-bsky-graph-get-followers#responses)) and returning a flat "normalized" dict composed of all [PARTIAL_PROFILE_FIELDS](#partial_profile_fields) keys. Be careful not to confuse with the [normalize_profile](#normalize_profile) function which operate on the full version of the profile data, retrieved from [`app.bsky.actor.getProfiles` HTTP endpoint](docs.bsky.app/docs/api/app-bsky-actor-get-profiles#responses) for example.

Will return datetimes as UTC but can take an optional second `locale` argument as a [`pytz`](https://pypi.org/project/pytz/) string timezone.

*Arguments*

* **data** *(dict)*: user profile data payload coming from Bluesky API.
* **locale** *(pytz.timezone as str, optional)*: timezone used to convert dates. If not given, will default to UTC.

### normalize_post

Function taking a nested dict describing a post from Bluesky's JSON payload and returning a flat "normalized" dict composed of all [POST_FIELDS](#post_fields) keys.

Will return datetimes as UTC but can take an optional last `locale` argument as a `pytz` string timezone.

When setting `extract_referenced_posts` to `True` it will instead return a list of dicts including the desired post as well as each referenced ones such as quoted posts and potentially parent posts of a conversation when the data comes from a Bluesky `feed` payload.

*Arguments*

* **payload** *(dict)*: post or feed data payload coming from Bluesky API.
* **locale** *(pytz.timezone as str, optional)*: timezone used to convert dates. If not given, will default to UTC.
* **extract_referenced_posts** *(bool, optional)*: whether to return in the output, in addition to the post to be normalized, also normalized data for each other referenced posts found in the payload data (including potentially other quoted posts as well as the parent and root posts of a thread if the post comes as an answer to another one). If `False`, the function will return a `dict`, if `True` a `list` of `dict`. Defaults to `False`.
* **collection_source** *(string, optional)*: An optional information to add within the `collected_via` field of the normalized post to indicate whence it was collected.

### transform_profile_into_csv_dict

Function transforming (i.e. mutating, so beware) a given normalized Bluesky profile into a suitable dict able to be written by a `csv.DictWriter` as a row.

Will convert list elements of the normalized data into a string with all elements separated by the `|` character, which can be changed using an optional `plural_separator` argument.

### transform_partial_profile_into_csv_dict

Function transforming (i.e. mutating, so beware) a given normalized Bluesky partial profile into a suitable dict able to be written by a `csv.DictWriter` as a row.

Will convert list elements of the normalized data into a string with all elements separated by the `|` character, which can be changed using an optional `plural_separator` argument.

### transform_post_into_csv_dict

Function transforming (i.e. mutating, so beware) a given normalized Bluesky post into a suitable dict able to be written by a `csv.DictWriter` as a row.

Will convert list elements of the normalized data into a string with all elements separated by the `|` character, which can be changed using an optional `plural_separator` argument.

### format_profile_as_csv_row

Function formatting the given normalized Bluesky profile as a list able to be written by a `csv.writer` as a row in the order of [PROFILE_FIELDS](#profile_fields) (which can therefore be used as header row of the CSV).

Will convert list elements of the normalized data into a string with all elements separated by the `|` character, which can be changed using an optional `plural_separator` argument.

### format_partial_profile_as_csv_row

Function formatting the given normalized Bluesky partial profile as a list able to be written by a `csv.writer` as a row in the order of [PARTIAL_PROFILE_FIELDS](#partial_profile_fields) (which can therefore be used as header row of the CSV).

Will convert list elements of the normalized data into a string with all elements separated by the `|` character, which can be changed using an optional `plural_separator` argument.

### format_post_as_csv_row

Function formatting the given normalized tBluesky post as a list able to be written by a `csv.writer` as a row in the order of [POST_FIELDS](#post_fields) (which can therefore be used as header row of the CSV).

Will convert list elements of the normalized data into a string with all elements separated by the `|` character, which can be changed using an optional `plural_separator` argument.

### PROFILE_FIELDS

List of a Bluesky user profile's normalized field names. Useful to declare headers with csv writers. Be careful not to confuse with [PARTIAL_PROFILE_FIELDS](#partial_profile_fields) which correspond to a lighter version of the profile data, retrieved from [follower/follow profile payloads](https://docs.bsky.app/docs/api/app-bsky-graph-get-followers#responses) for example.

### PARTIAL_PROFILE_FIELDS

List of a Bluesky user partial profile's (retrieved from [`app.bsky.graph.getFollowers` HTTP endpoint](https://docs.bsky.app/docs/api/app-bsky-graph-get-followers#responses) for example) normalized field names. Useful to declare headers with csv writers. Be careful not to confuse with [PROFILE_FIELDS](#profile_fields) which correspond to the full version of the profile data, retrieved from [`app.bsky.actor.getProfiles` HTTP endpoint](docs.bsky.app/docs/api/app-bsky-actor-get-profiles#responses) for example.

### POST_FIELDS

List of a Bluesky post's normalized field names. Useful to declare headers with csv writers.

### normalize_user

Function taking a nested dict describing a user from Twitter's JSON payload and returning a flat "normalized" dict composed of all [USER_FIELDS](#user_fields) keys.

Will return datetimes as UTC but can take an optional second `locale` argument as a [`pytz`](https://pypi.org/project/pytz/) string timezone.

*Arguments*

* **data** *(dict)*: user profile data payload coming from Twitter API v1.1 or v2.
* **locale** *(pytz.timezone as str, optional)*: timezone used to convert dates. If not given, will default to UTC.
* **pure** *(bool, optional)*: whether to allow the function to mutate its original `data` argument. Defaults to `True`.
        
### normalize_tweet

Function taking a nested dict describing a tweet from Twitter's JSON payload (API v1.1) and returning a flat "normalized" dict composed of all [TWEET_FIELDS](#tweet_fields) keys.

Will return datetimes as UTC but can take an optional last `locale` argument as a `pytz` string timezone.

When setting `extract_referenced_posts` to `True` it will instead return a list of dicts including the desired tweet as well as each referenced ones such as quoted or retweeted tweets.

*Arguments*

* **tweet** *(dict)*: tweet data payload coming from Twitter API v1.1.
* **locale** *(pytz.timezone as str, optional)*: timezone used to convert dates. If not given, will default to UTC.
* **extract_referenced_posts** *(bool, optional)*: whether to return in the output, in addition to the tweet to be normalized, also normalized data for each other referenced tweets found in the payload data (including retweeted and quoted tweets). If `False`, the function will return a `dict`, if `True` a `list` of `dict`. Defaults to `False`.
* **collection_source** *(string, optional)*: An optional information to add within the `collected_via` field of the normalized tweet to indicate whence it was collected.

### normalize_tweets_payload_v2

Function taking an entire tweets JSON payload from Twitter API v2 and returning a list of all contained tweets formatted as flat "normalized" dicts composed of all [TWEET_FIELDS](#tweet_fields) keys.

Will return datetimes as UTC but can take an optional last `locale` argument as a `pytz` string timezone.

When setting `extract_referenced_posts` to `True` it will instead return a list of dicts including the desired tweets as well as each referenced ones such as quoted or retweeted tweets.

*Arguments*

* **payload** *(dict)*: tweets data payload coming from Twitter API v2.
* **locale** *(pytz.timezone, optional)*: timezone used to convert dates. If not given, will default to UTC.
* **extract_referenced_tweets** *(bool, optional)*: whether to return in the output, in addition to the tweet to be normalized, also normalized data for each other referenced tweets found in the payload data (including retweeted and quoted tweets).
* **collection_source** *(string, optional)*: An optional information to add within the `collected_via` field of the normalized tweet to indicate whence it was collected.

```python
from twitwi import normalize_tweets_payload_v2

# Normalizing an entire tweets payload to extract a list of tweets
normalize_tweets_payload_v2(payload)

# Normalizing an entire tweets payload to extract a list of tweets
# as well as the referenced tweets (quoted, retweeted, etc.)
normalize_tweets_payload_v2(payload, extract_referenced_tweets=True)

# Converting found dates to a chosen timezone
from pytz import timezone
paris_tz = timezone('Europe/Paris')

normalize_tweets_payload_v2(payload, locale=paris_tz)
```

### transform_user_into_csv_dict

Function transforming (i.e. mutating, so beware) a given normalized Twitter user into a suitable dict able to be written by a `csv.DictWriter` as a row.
Will convert list elements of the normalized data into a string with all elements separated by the `|` character, which can be changed using an optional `plural_separator` argument.

```python
from twitwi import transform_user_into_csv_dict

# The function returns nothing, `normalized_user` has been mutated
transform_user_into_csv_dict(normalized_user)
```

### transform_tweet_into_csv_dict

Function transforming (i.e. mutating, so beware) a given normalized tweet into a suitable dict able to be written by a `csv.DictWriter` as a row.

Will convert list elements of the normalized data into a string with all elements separated by the `|` character, which can be changed using an optional `plural_separator` argument.

```python
from twitwi import transform_tweet_into_csv_dict

# The function returns nothing, `normalized_tweet` has been mutated
transform_tweet_into_csv_dict(normalized_tweet)
```

### format_user_as_csv_row

Function formatting the given normalized Twitter user as a list able to be written by a `csv.writer` as a row.

Will convert list elements of the normalized data into a string with all elements separated by the `|` character, which can be changed using an optional `plural_separator` argument.

```python
from twitwi import format_user_as_csv_row

row = format_user_as_csv_row(normalized_user)
```

### format_tweet_as_csv_row

Function formatting the given normalized tweet as a list able to be written by a `csv.writer` as a row.

Will convert list elements of the normalized data into a string with all elements separated by the `|` character, which can be changed using an optional `plural_separator` argument.

```python
from twitwi import format_tweet_as_csv_row

row = format_tweet_as_csv_row(normalized_tweet)
```

### apply_tcat_format

Function taking a normalized tweet and returning a new dict with keys adjusted to correspond to [DMI's TCAT](https://github.com/digitalmethodsinitiative/dmi-tcat) format.

```python
from twitwi import apply_tcat_format

tweet_tcat = apply_tcat_format(normalized_tweet)
```

### USER_FIELDS

List of a Twitter user profile's field names. Useful to declare headers with csv writers:

```python
from twitwi.constants import USER_FIELDS

# Using csv.writer
w = csv.writer(f)
w.writerow(USER_FIELDS)

# Using csv.DictWriter
w = csv.DictWriter(f, fieldnames=USER_FIELDS)
w.writeheader()
```

### TWEET_FIELDS

List of a tweet's field names. Useful to declare headers with csv writers:

```python
from twitwi.constants import TWEET_FIELDS

# Using csv.writer
w = csv.writer(f)
w.writerow(TWEET_FIELDS)

# Using csv.DictWriter
w = csv.DictWriter(f, fieldnames=TWEET_FIELDS)
w.writeheader()
```

### anonymize_normalized_tweet

Function taking a normalized tweet and mutating it by editing the text and removing all metadata related to the tweet's author user.

Note that the tweet's ID as well as other users screennames mentioned in the tweet are kept and could require extra processing depending on the use cases.

```python
from twitwi import anonymize_normalized_tweet

# The function returns nothing, `normalized_tweet` has been mutated
anonymize_normalized_tweet(normalized_tweet)
```

### get_timestamp_from_id

Function taking a tweet ID and producing from it the UTC UNIX timestamp of when the tweet was posted.

This relies on the Snowflake format used by Twitter to generate tweets IDs, which builds IDs on top of the actual timestamp when a tweet was submitted.

Will only work for tweets with an ID greater than 29700859247, which is the first ID from which the Snowflake algorithm was implemented.

```python
from twitwi import get_timestamp_from_id

timestamp = get_timestamp_from_id(tweet_ID)
```

### get_dates_from_id

Function taking a tweet ID and producing from it the datetime when the tweet was posted.

This relies on the Snowflake format used by Twitter to generate tweets IDs, which builds IDs on top of the actual timestamp when a tweet was submitted.

Will only work for tweets with an ID greater than 29700859247, which is the first ID from which the Snowflake algorithm was implemented.

The function can also take an optional `locale` argument as a [`pytz`](https://pypi.org/project/pytz/) string timezone.

```python
from twitwi import get_dates_from_id

date_time = get_dates_from_id(tweet_ID)

# Or converting to a chosen timezone
from pytz import timezone
paris_tz = timezone('Europe/Paris')

date_time = get_dates_from_id(tweet_ID, locale=paris_tz)
```
