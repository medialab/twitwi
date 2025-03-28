from typing import TypedDict, List, Optional


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
    collection_time: Optional[str]


class BlueskyPost(TypedDict):
    cid: str
    did: str
    url: str
    uri: str
    timestamp_utc: int
    local_time: str
    user_did: str
    user_handle: str
    text: str
    repost_count: int
    like_count: int
    reply_count: int
    quote_count: int
    user_name: str
    # user_description: str
    # user_url: str
    user_image: str
    # user_posts: int
    # user_followers: int
    # user_friends: int
    # user_likes: int
    user_created_at: str
    user_timestamp_utc: int
    user_langs: List[str]
    # to_user_handle: Optional[str]
    to_user_did: Optional[str]
    to_post_cid: Optional[str]
    to_post_did: Optional[str]
    # to_post_url: Optional[str]
    # to_root_user_handle: Optional[str]
    to_root_user_did: Optional[str]
    to_root_post_cid: Optional[str]
    to_root_post_did: Optional[str]
    # to_root_post_url: Optional[str]
    reposted_did: str
    reposted_user_handle: str
    reposted_user_did: str
    reposted_timestamp_utc: int
    quoted_did: str
    quoted_user_handle: str
    quoted_user_did: str
    quoted_timestamp_utc: int
    links: List[str]
    domains: List[str]
    media_urls: List[str]
    media_files: List[str]
    media_types: List[str]
    media_alt_texts: List[str]
    mentioned_user_handles: List[str]
    mentioned_user_dids: List[str]
    hashtags: List[str]
    collection_time: Optional[str]
    collected_via: Optional[List[str]]
    match_query: Optional[str]
