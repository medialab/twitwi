from typing import Dict, Union

from twitwi.utils import get_dates
from twitwi.bluesky.types import BlueskyProfile


def normalize_profile(data: Dict, locale: Union[str, None] = None) -> BlueskyProfile:
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
