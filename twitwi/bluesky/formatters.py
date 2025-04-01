from typing import List

from twitwi.bluesky.constants import PROFILE_FIELDS, POST_FIELDS, POST_LIST_FIELDS
from twitwi.bluesky.types import BlueskyProfile, BlueskyPost


def format_profile_as_csv_row(data: BlueskyProfile) -> List:
    return [data.get(field, "") for field in PROFILE_FIELDS]


def format_post_as_csv_row(data: BlueskyPost) -> List:
    # TODO: handle other field types than str, maybe reuse formater functions from twitwi/formatters
    return [
        data.get(field, "")
        if field not in POST_LIST_FIELDS
        else "|".join(data.get(field, []))
        for field in POST_FIELDS
    ]
