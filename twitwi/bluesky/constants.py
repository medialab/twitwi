from typing import List, Optional

from twitwi.bluesky.types import BlueskyProfile, BlueskyMinimalProfile, BlueskyPost

PROFILE_FIELDS = list(BlueskyProfile.__annotations__.keys())

MINIMAL_PROFILE_FIELDS = list(BlueskyMinimalProfile.__annotations__.keys())

POST_FIELDS = list(BlueskyPost.__annotations__.keys())

POST_PLURAL_FIELDS = [
    k
    for k, v in BlueskyPost.__annotations__.items()
    if v == List[str] or v == Optional[List[str]]
]

POST_BOOLEAN_FIELDS = [
    k
    for k, v in BlueskyPost.__annotations__.items()
    if v is bool or v == Optional[bool]
]
