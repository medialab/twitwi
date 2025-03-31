from typing import List, Optional

from twitwi.bluesky.types import BlueskyProfile, BlueskyPost

PROFILE_FIELDS = list(BlueskyProfile.__annotations__.keys())

POST_FIELDS = list(BlueskyPost.__annotations__.keys())

POST_LIST_FIELDS = [
    k
    for k, v in BlueskyPost.__annotations__.items()
    if v == List[str] or v == Optional[List[str]]
]
