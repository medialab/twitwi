from typing import TypedDict, List, Optional


class BlueskyProfile(TypedDict):
    did: str
    url: str
    handle: str
    display_name: str
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
    created_at: str
    timestamp_utc: int
    collection_time: Optional[str]


class BlueskyPost(TypedDict):
    cid: str
    did: str
    uri: str
    url: str
    timestamp_utc: int
    local_time: str
    user_did: str
    user_handle: str
    text: str
    original_text: str
    repost_count: int
    like_count: int
    reply_count: int
    quote_count: int
    user_url: str
    user_diplay_name: str
    # user_description: str
    # user_posts: int
    # user_followers: int
    # user_follows: int
    # user_lists: int
    user_langs: List[str]
    user_avatar: str
    user_created_at: str
    user_timestamp_utc: int
    to_post_cid: Optional[str]
    to_post_did: Optional[str]
    to_post_uri: Optional[str]
    to_post_url: Optional[str]
    to_user_did: Optional[str]
    # to_user_handle: Optional[str]
    to_root_post_cid: Optional[str]
    to_root_post_did: Optional[str]
    to_root_post_uri: Optional[str]
    to_root_post_url: Optional[str]
    to_root_user_did: Optional[str]
    # to_root_user_handle: Optional[str]
    reposted_cid: Optional[str]
    reposted_did: Optional[str]
    reposted_uri: Optional[str]
    reposted_url: Optional[str]
    reposted_user_handle: Optional[str]
    reposted_user_did: Optional[str]
    reposted_timestamp_utc: Optional[int]
    quoted_cid: Optional[str]
    quoted_did: Optional[str]
    quoted_uri: Optional[str]
    quoted_url: Optional[str]
    quoted_user_handle: Optional[str]
    quoted_user_did: Optional[str]
    quoted_timestamp_utc: Optional[int]
    quoted_status: Optional[str]
    links: List[str]
    domains: List[str]
    card_link: Optional[str]
    card_title: Optional[str]
    card_description: Optional[str]
    card_thumbnail: Optional[str]
    media_urls: List[str]
    media_thumbnails: List[str]
    media_types: List[str]
    media_alt_texts: List[str]
    mentioned_user_handles: List[str]
    mentioned_user_dids: List[str]
    hashtags: List[str]
    replies_rules: Optional[List[str]]
    replies_rules_created_at: Optional[str]
    replies_rules_timestamp_utc: Optional[int]
    hidden_replies: Optional[List[str]]
    # quotes_rule: Optional[str]
    # quotes_rules_created_at: Optional[str]
    # quotes_rules_timestamp_utc: Optional[int]
    # detached_quotes: Optional[List[str]]
    collection_time: Optional[str]
    collected_via: Optional[List[str]]
    match_query: Optional[str]
