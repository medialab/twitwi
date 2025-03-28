from typing import Dict, Optional

from twitwi.utils import get_collection_time, get_dates
from twitwi.bluesky.utils import validate_post_payload
from twitwi.bluesky.types import BlueskyProfile, BlueskyPost


def normalize_profile(data: Dict, locale: Optional[str] = None) -> BlueskyProfile:
    associated = data["associated"]

    pinned_post_uri = None
    pinned_post_data = data.get("pinnedPost")

    if pinned_post_data is not None:
        pinned_post_uri = pinned_post_data["uri"]

    timestamp_utc, created_at = get_dates(
        data["createdAt"], locale=locale, source="bluesky"
    )

    return {
        "did": data["did"],
        "handle": data["handle"],
        "display_name": data["displayName"],
        "created_at": created_at,
        "timestamp_utc": timestamp_utc,
        "description": data["description"],
        "avatar": data["avatar"],
        "posts": data["postsCount"],
        "followers": data["followersCount"],
        "follows": data["followsCount"],
        "lists": associated["lists"],
        "feedgens": associated["feedgens"],
        "starter_packs": associated["starterPacks"],
        "banner": data["banner"],
        "pinned_post_uri": pinned_post_uri,
        "collection_time": get_collection_time()
    }


def parse_post_uri(uri):
    """Returns a tuple of (author_did, post_did) from an at:// post URI"""

    if not uri.startswith("at://") and "/app.bsky.feed.post/" not in uri:
        raise Exception(f"Not a Bluesky post uri: {uri}")
    return uri[5:].split("/app.bsky.feed.post/")


def format_post_url(user_handle, post_did):
    return f"https://bsky.app/profile/{user_handle}/post/{post_did}"


def normalize_post(data: Dict, locale: Optional[str] = None) -> BlueskyPost:

    if not validate_post_payload(data):
        raise TypeError("data provided to normalize_post is not a standard Bluesky post payload")

    post = {}

    # Handle datetime fields
    post["collection_time"] = get_collection_time()
    post["timestamp_utc"], post["local_time"] = get_dates(
        data["record"]["createdAt"], locale=locale, source="bluesky"
    )

    # Handle post/user identifiers
    post["cid"] = data["cid"]
    post["uri"] = data["uri"]
    post["user_handle"] = data["author"]["handle"]
    post["user_did"], post["did"] = parse_post_uri(data["uri"])
    post["url"] = format_post_url(post["user_handle"], post["did"])

    if post["user_did"] != data["author"]["did"]:
        raise Exception(
            f"Inconsistent user did between Bluesky post uri and post's author metadata: {data['uri']}"
        )

    # Handle user metadata
    post["user_name"] = data["author"]["displayName"]
    post["user_image"] = data["author"]["avatar"]
    post["user_timestamp_utc"], post["user_created_at"] = get_dates(
        data["author"]["createdAt"], locale=locale, source="bluesky"
    )
    post["user_langs"] = data["record"]["langs"]

    # Handle metrics
    post["repost_count"] = data["repostCount"]
    post["reply_count"] = data["replyCount"]
    post["like_count"] = data["likeCount"]
    post["quote_count"] = data["quoteCount"]

    # Handle thread info when applicable
    if "reply" in data["record"]:
        if "parent" in data["record"]["reply"]:
            post["to_user_did"], post["to_post_did"] = parse_post_uri(data["record"]["reply"]["parent"]["uri"])
            post["to_post_cid"] = data["record"]["reply"]["parent"]["cid"]
        if "root" in data["record"]["reply"]:
            post["to_root_user_did"], post["to_root_post_did"] = parse_post_uri(data["record"]["reply"]["root"]["uri"])
            post["to_root_post_cid"] = data["record"]["reply"]["root"]["cid"]

    # TODO: handle quotes

    # TODO: handle reposts when we can find some in payloads (from user timeline maybe?)

    # TODO: handle links

    # TODO: handle medias

    # TODO: handle mentions

    # TODO: handle hashtags

    # TODO: complete text with links/medias/quotes when necessary
    post["text"] = data["record"]["text"]

    return post
