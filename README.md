[![Build Status](https://travis-ci.org/medialab/twitwi.svg)](https://travis-ci.org/medialab/twitwi)

# Twitwi

A collection of Twitter-related helper functions for python.

## Installation

You can install `twitwi` with pip with the following command:

```
pip install twitwi
```

## Usage

* [normalize_tweets_payload_v2](#normalize_tweets_payload_v2)

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
