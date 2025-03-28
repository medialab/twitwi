from typing import List

from twitwi.bluesky.types import BlueskyProfile, BlueskyPost

PROFILE_FIELDS = list(BlueskyProfile.__annotations__.keys())

POST_FIELDS = list(BlueskyPost.__annotations__.keys())

POST_LIST_FIELDS = [k for k, v in BlueskyPost.__annotations__.items() if v == List[str]]
