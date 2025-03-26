import re

QUOTED_REDACT_RE = re.compile(r"«\s+[^»]+:\s+([^»]+)\s+»")


def redact_quoted_text(text: str) -> str:
    return QUOTED_REDACT_RE.sub(r"« \1 »", text)


def redact_rt_text(text: str) -> str:
    return "RT: " + text.split(": ", 1)[1]


FIELDS_TO_DELETE = [
    # The tweet's url leaks the user
    "url",
    # User's place
    "lat",
    "lng",
    "place_coordinates",
    "place_country_code",
    "place_name",
    "place_type",
    "user_location",
    # User info
    "user_created_at",
    "user_description",
    "user_id",
    "user_image",
    "user_name",
    "user_screen_name",
    "user_timestamp_utc",
    "user_url",
    "user_verified",
    # Retweeted user info
    "retweeted_timestamp_utc",
    "retweeted_user",
    "retweeted_user_id",
    # Replied user info
    "to_userid",
    "to_username",
    # Quoted user info
    "quoted_user",
    "quoted_user_id",
    "quoted_timestamp_utc",
]


# NOTE: currently we still keep the id, but we should drop it
# to really call this an anonymized tweet.
# NOTE: we do not redact mentions either.
# NOTE: we also don't redact replies.
def anonymize_normalized_tweet(normalized_tweet) -> None:
    # Text mangling
    text = normalized_tweet["text"]

    if normalized_tweet.get("retweeted_id", None) is not None:
        normalized_tweet["text"] = redact_rt_text(text)

    elif normalized_tweet.get("quoted_id", None) is not None:
        normalized_tweet["text"] = redact_quoted_text(text)

    for field in FIELDS_TO_DELETE:
        if field in normalized_tweet:
            del normalized_tweet[field]
