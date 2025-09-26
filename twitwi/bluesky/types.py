from typing import TypedDict, List, Optional


# To know more about Bluesky IDs:
# - https://docs.bsky.app/docs/advanced-guides/resolving-identities
# - https://bluesky.idunno.dev/docs/commonTerms.html

class BlueskyProfile(TypedDict):
    did: str                            # persistent long-term identifier of the account
    url: str                            # URL of the profile accessible on the web
    handle: str                         # updatable human-readable username of the account (usually like username.bsky.social or username.com)
    display_name: Optional[str]         # updatable human-readable name of the account
    description: Optional[str]          # profile short description written by the user
    posts: int                          # total number of posts submitted by the user (at collection time)
    followers: int                      # total number of followers of the user (at collection time)
    follows: int                        # total number of other users followed by the user (at collection time)
    lists: int                          # total number of lists created by the user (at collection time)
    feedgens: int                       # total number of custom feeds created by the user (at collection time)
    starter_packs: int                  # total number of starter packs created by the user (at collection time)
    avatar: Optional[str]               # URL to the image serving as avatar to the user
    banner: Optional[str]               # URL to the image serving as profile banner to the user
    pinned_post_uri: Optional[str]      # ATProto's internal URI to the post potentially pinned by the user to appear at the top of his posts on his profile
    created_at: str                     # datetime (potentially timezoned) of when the user created the account
    timestamp_utc: int                  # Unix UTC timestamp of when the user created the account
    collection_time: Optional[str]      # datetime (potentially timezoned) of when the data was normalized

class BlueskyPartialProfile(TypedDict): # A partial version of the profile found in follower/follow profile payloads
    did: str                            # persistent long-term identifier of the account
    url: str                            # URL of the profile accessible on the web
    handle: str                         # updatable human-readable username of the account (usually like username.bsky.social or username.com)
    display_name: Optional[str]         # updatable human-readable name of the account
    description: Optional[str]          # profile short description written by the user
    lists: Optional[int]                # total number of lists created by the user (at collection time)
    feedgens: Optional[int]             # total number of custom feeds created by the user (at collection time)
    starter_packs: Optional[int]        # total number of starter packs created by the user (at collection time)
    avatar: Optional[str]               # URL to the image serving as avatar to the user
    created_at: str                     # datetime (potentially timezoned) of when the user created the account
    timestamp_utc: int                  # Unix UTC timestamp of when the user created the account
    collection_time: Optional[str]      # datetime (potentially timezoned) of when the data was normalized



class BlueskyPost(TypedDict):
    # Identifying fields
    cid: str                            # internal content identifier of the post
    did: str                            # persistent long-term identifier of the post
    uri: str                            # ATProto's internal URI to the post
    url: str                            # URL of the post accessible on the web

    # Datetime fields
    timestamp_utc: int                  # Unix UTC timestamp of when the post was submitted
    local_time: str                     # datetime (potentially timezoned) of when the post was submitted

    # Author identifying fields
    user_did: str                       # persistent long-term identifier of the account who authored the post
    user_handle: str                    # updatable human-readable username of the account who authored the post

    # Content fields
    text: str                           # reprocessed complete text of the post, including full links, full text of the quoted post (recursively up to 3 posts) and links to images or videos included within
    original_text: str                  # original text of the post as returned by the Bluesky API

    # Metrics fields
    repost_count: int                   # total number of reposts of the post (at collection time)
    like_count: int                     # total number of likes received by the post (at collection time)
    reply_count: int                    # total number of replies received by the post (at collection time)
    quote_count: int                    # total number of posts the post was quoted into (at collection time)

    # Extra field
    bridgy_original_url: Optional[str]  # source of the original post when it was posted from another platform such as Mastodon via the Bridgy connection tool

    # Author metadata fields
    user_url: str                       # URL of the profile accessible on the web of the account who authored the post
    user_diplay_name: str               # updatable human-readable name of the account who authored the post
    # user_description: str             # not available from posts payloads
    # user_posts: int                   # not available from posts payloads
    # user_followers: int               # not available from posts payloads
    # user_follows: int                 # not available from posts payloads
    # user_lists: int                   # not available from posts payloads
    user_langs: List[str]               # languages in which the author of the posts usually writes posts (declarative)
    user_avatar: Optional[str]          # URL to the image serving as avatar to the user who authored the post
    user_created_at: str                # datetime (potentially timezoned) of when the user who authored the post created the account
    user_timestamp_utc: int             # Unix UTC timestamp of when the user who authored the post created the account

    # Parent post identifying fields
    # (if the post comes in a conversation as an answer to another post)
    to_post_cid: Optional[str]          # internal content identifier of the parent post
    to_post_did: Optional[str]          # persistent long-term identifier of the parent post
    to_post_uri: Optional[str]          # ATProto's internal URI of the parent post
    to_post_url: Optional[str]          # URL of the parent post on the web
    to_user_did: Optional[str]          # persistent long-term identifier of the account who authored the parent post
    # to_user_handle: Optional[str]     # not available from posts payloads, cf https://github.com/bluesky-social/atproto/issues/3722

    # Root conversation post identifying fields
    # (if the post comes in a conversation, this post is the first one that initiated the thread)
    to_root_post_cid: Optional[str]         # internal content identifier of the root conversation post
    to_root_post_did: Optional[str]         # persistent long-term identifier of the root conversation post
    to_root_post_uri: Optional[str]         # ATProto's internal URI of the root conversation post
    to_root_post_url: Optional[str]         # URL of the root conversation post on the web
    to_root_user_did: Optional[str]         # persistent long-term identifier of the account who authored the root conversation post
    # to_root_user_handle: Optional[str]    # not available from posts payloads, cf https://github.com/bluesky-social/atproto/issues/3722

    # Repost metadata fields
    # Contrary to Twitter where a retweet is a new tweet with its own ID, reposting on Bluesky only adds a flag to the post saying it was reposted by a specific user at a specific time. These are available for instance when collecting a user's feed.
    repost_by_user_did: Optional[str]       # persistent long-term identifier of the account who reposted the post
    repost_by_user_handle: Optional[str]    # updatable human-readable username of the account who reposted the post
    repost_created_at: Optional[int]        # datetime (potentially timezoned) of when the repost was done
    repost_timestamp_utc: Optional[int]     # Unix UTC timestamp of when the repost was done

    # Quoted post metadata fields
    # (when a post embeds another one)
    quoted_cid: Optional[str]           # internal content identifier of the quoted post
    quoted_did: Optional[str]           # persistent long-term identifier of the quoted post
    quoted_uri: Optional[str]           # ATProto's internal URI to the quoted post
    quoted_url: Optional[str]           # URL of the quoted post accessible on the web
    quoted_user_did: Optional[str]      # persistent long-term identifier of the account who authored the quoted post
    quoted_user_handle: Optional[str]   # updatable human-readable username of the account who authored the quoted post
    quoted_created_at: Optional[int]    # datetime (potentially timezoned) of when the quoted post was submitted
    quoted_timestamp_utc: Optional[int] # Unix UTC timestamp of when the quoted post was submitted
    quoted_status: Optional[str]        # empty or "detached" when the author of the quoted post intentionnally required the quoting post not to appear in the list of this post's quotes

    # Embedded elements metadata fields
    links: List[str]                    # list of URLs of all links shared within the post (including potentially the embedded card detailed below, but not the link to a potential quoted post)
    domains: List[str]                  # list of domains of the links shared within the post (here a domain refers to a full hostname, including subdomains, for instance bluesky.com or medialab.sciencespo.fr)
    card_link: Optional[str]            # URL of the link displayed as a card within the post if any
    card_title: Optional[str]           # title of the webpage corresponding to the linkg diplayed as a card within the post if any
    card_description: Optional[str]     # description of the webpage corresponding to the linkg diplayed as a card within the post if any
    card_thumbnail: Optional[str]       # image displayed as an illustration of the webpage corresponding to the link diplayed as a card within the post if any
    media_urls: List[str]               # list of URLs to all media (images, videos, gifs) embedded in the post
    media_thumbnails: List[str]         # list of URLs to small thumbnail version of all media (images, videos, gifs) embedded in the post
    media_types: List[str]              # MIME types (such as image/jpeg, image/gif, video/mp4, etc.) of all media (images, videos, gifs) embedded in the post
    media_alt_texts: List[str]          # description texts of all media (images, videos, gifs) embedded in the post
    mentioned_user_dids: List[str]      # list of all persistent long-term identifiers of the accounts adressed within the post (does not include users to which the post replied)
    mentioned_user_handles: List[str]   # list of all updatable human-readable usernames of the accounts adressed within the post (does not include users to which the post replied)
    hashtags: List[str]                 # list of all unique lowercased hashtags found within the post's text

    # Conversation rules fields
    replies_rules: Optional[List[str]]          # list of specific conversation rules set by the author for the current post (can be one or a combination of: disallow, allow_from_follower, allow_from_following, allow_from_mention, or allow_from_list: followed by a list of user DIDs)
    replies_rules_created_at: Optional[str]     # datetime (potentially timezoned) of when the user set the replies_rules
    replies_rules_timestamp_utc: Optional[int]  # Unix UTC timestamp of when the user set the replies_rules
    hidden_replies_uris: Optional[List[str]]    # list of ATProto's internal URIs to posts who replied to the post, but where intentionnally marked as hidden by the current post's author
    # quotes_rule: Optional[str]                # not available from posts payloads, cf https://github.com/bluesky-social/atproto/issues/3712
    # quotes_rules_created_at: Optional[str]    # not available from posts payloads, cf https://github.com/bluesky-social/atproto/issues/3712
    # quotes_rules_timestamp_utc: Optional[int] # not available from posts payloads, cf https://github.com/bluesky-social/atproto/issues/3712
    # detached_quotes: Optional[List[str]]      # not available from posts payloads, cf https://github.com/bluesky-social/atproto/issues/3712

    # Extra fields linked to the data collection and processing
    collection_time: Optional[str]      # datetime (potentially timezoned) of when the data was normalized
    collected_via: Optional[List[str]]  # extra field added by the normalization process to express how the data collection was ran, will be "quote" or "thread" when a post was grabbed as a referenced post within the originally collected post using the "extract_referenced_posts" option of "normalize_post"
    match_query: Optional[bool]         # extra field added by the normalization process to express whether the post was an intentionnally collected one or only came as a referenced post within the originally collected post using the "extract_referenced_posts" option of "normalize_post"
