from typing import TypedDict, Optional


class BlueskyProfile(TypedDict):
    did: str
    handle: str
    display_name: str
    created_at: str
    timestamp_utc: int
    description: str
    posts: int
    followers: int
    follows: int
    lists: int
    feedgens: int
    starter_packs: int
    avatar: str
    banner: str
    pinned_post_uri: Optional[str]
