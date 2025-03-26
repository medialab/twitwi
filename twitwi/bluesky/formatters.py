from typing import List

from twitwi.bluesky.constants import PROFILE_FIELDS
from twitwi.bluesky.types import BlueskyProfile


def format_profile_as_csv_row(data: BlueskyProfile) -> List:
    return [data.get(field, "") for field in PROFILE_FIELDS]
