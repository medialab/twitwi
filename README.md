[![Build Status](https://github.com/medialab/twitwi/workflows/Tests/badge.svg)](https://github.com/medialab/twitwi/actions)

# Twitwi

A collection of Twitter-related helper functions for python.

## Installation

You can install `twitwi` with pip with the following command:

```
pip install twitwi
```

## Usage

*Normalization functions*

* [normalize_tweets_payload_v2](#normalize_tweets_payload_v2)

*Formatting functions*

* [transform_tweet_into_csv_dict](#transform_tweet_into_csv_dict)
* [transform_user_into_csv_dict](#transform_user_into_csv_dict)
* [format_tweet_as_csv_row](#format_tweet_as_csv_row)

*Useful constants (under twitwi.constants)*

* [TWEET_FIELDS](#tweet_fields)
* [USER_FIELDS](#user_fields)

### normalize_tweets_payload_v2

Function taking an entire tweets payload from the v2 API and returning a list of the contained tweets normalized and structured in a way that makes further analysis of the data convenient.

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

*Arguments*

* **payload** *(dict)*: tweets payload coming from Twitter API v2.
* **locale** *(pytz.timezone, optional)*: timezone used to convert dates. If not given, will default to UTC.
* **extract_referenced_tweets** *(bool, optional)*: whether to keep referenced tweets (retweeted, quoted etc.) in the output. Defaults to `False`.
* **collection_source** *(string, optional): An optional information to add to the tweets to indicate whence you collected them.

### transform_tweet_into_csv_dict

Function transforming (i.e. mutating, so beware) a given normalized tweet into a suitable dict able to be written by a `csv.DictWriter` as a row.

```python
from twitwi import transform_tweet_into_csv_dict

# The function returns nothing, `normalized_tweet` has been mutated
transform_tweet_into_csv_dict(normalized_tweet)
```

### transform_user_into_csv_dict

Function transforming (i.e. mutating, so beware) a given normalized Twitter user into a suitable dict able to be written by a `csv.DictWriter` as a row.

```python
from twitwi import transform_user_into_csv_dict

# The function returns nothing, `normalized_user` has been mutated
transform_user_into_csv_dict(normalized_user)
```

### format_tweet_as_csv_row

Function formatting the given normalized tweet as a list able to be written by a `csv.writer` as a row.

```python
from twitwi import format_tweet_as_csv_row

row = format_tweet_as_csv_row(normalized_tweet)
```

### format_user_as_csv_row

Function formatting the given normalized Twitter user as a list able to be written by a `csv.writer` as a row.

```python
from twitwi import format_user_as_csv_row

row = format_user_as_csv_row(normalized_user)
```

### TWEET_FIELDS

List of tweet field names. Useful to declare headers with csv writers:

```python
from twitwi.constants import TWEET_FIELDS

# Using csv.writer
w = csv.writer(f)
w.writerow(TWEET_FIELDS)

# Using csv.DictWriter
w = csv.DictWriter(f, fieldnames=TWEET_FIELDS)
w.writeheader()
```

### USER_FIELDS

```python
from twitwi.constants import USER_FIELDS

# Using csv.writer
w = csv.writer(f)
w.writerow(USER_FIELDS)

# Using csv.DictWriter
w = csv.DictWriter(f, fieldnames=USER_FIELDS)
w.writeheader()
```
