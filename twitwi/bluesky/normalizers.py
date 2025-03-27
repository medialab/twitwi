from typing import Dict, Optional

from twitwi.utils import get_collection_time, get_dates
from twitwi.bluesky.types import BlueskyProfile, BlueskyPost


def normalize_profile(data: Dict, locale: Optional[str] = None) -> BlueskyProfile:
    associated = data["associated"]

    pinned_post_uri = None
    pinned_post_data = data.get("pinnedPost")

    if pinned_post_data is not None:
        pinned_post_uri = pinned_post_data["uri"]

    timestamp_utc, created_at = get_dates(data["createdAt"], locale=locale, source="bluesky")

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
    }


def parse_post_uri(uri):
    if not uri.startswith("at://") and "/app.bsky.feed.post/" not in uri:
        raise(Exception(f"Not a BlueSky post uri: {uri}"))
    pieces = uri[5:].split("/app.bsky.feed.post/")
    return {
        "user_did": pieces[0],
        "post_did": pieces[1]
    }


def format_post_url(user_handle, post_did):
    return f"https://bsky.app/profile/{user_handle}/post/{post_did}"


def normalize_post(data: Dict, locale: Optional[str] = None) -> BlueskyPost:

    post = {}

    post["collection_time"] = get_collection_time()

    post["cid"] = data["cid"]
    post["uri"] = data["uri"]

    post_dids = parse_post_uri(data["uri"])
    post["did"] = post_dids["post_did"]

    post["timestamp_utc"], post["local_time"] = get_dates(data["record"]["createdAt"], locale=locale, source="bluesky")

    post["user_did"] = post_dids["user_did"]
    if post["user_did"] != data["author"]["did"]:
        raise(Exception(f"Inconsistent user did between BlueSky post uri and post's author metadata: {data['uri']}"))

    post["user_handle"] = data["author"]["handle"]
    post["user_name"] = data["author"]["displayName"]
    post["user_image"] = data["author"]["avatar"]
    post["user_timestamp_utc"], post["user_created_at"] = get_dates(data["author"]["createdAt"], locale=locale, source="bluesky")
    post["user_langs"] = data["record"]["langs"]

    post["url"] = format_post_url(post["user_handle"], post["did"])

    return post

