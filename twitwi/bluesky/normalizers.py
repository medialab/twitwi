from typing import Dict, Optional

from twitwi.utils import (
    get_collection_time,
    get_dates,
    custom_normalize_url,
    custom_get_normalized_hostname,
)
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
        "collection_time": get_collection_time(),
    }


def parse_post_uri(uri):
    """Returns a tuple of (author_did, post_did) from an at:// post URI"""

    if not uri.startswith("at://") and "/app.bsky.feed.post/" not in uri:
        raise Exception(f"Not a Bluesky post uri: {uri}")
    return uri[5:].split("/app.bsky.feed.post/")


def format_post_url(user_handle, post_did):
    return f"https://bsky.app/profile/{user_handle}/post/{post_did}"


def format_media_url_and_file(user_did, media_cid, mime_type):
    media_type = mime_type.split("/")[1]
    if mime_type.startswith("image"):
        media_url = f"https://cdn.bsky.app/img/feed_fullsize/plain/{user_did}/{media_cid}@{media_type}"
    elif mime_type.startswith("video"):
        media_url = f"https://video.bsky.app/watch/{user_did}/{media_cid}/playlist.m3u8"
    else:
        raise Exception("Unusual media mimeType for post : %s" % (mime_type))

    user = user_did.replace("did:plc:", "")
    media_file = f"{user}_{media_cid}.{media_type}"
    return (media_url, media_file)


def normalize_post(data: Dict, locale: Optional[str] = None) -> BlueskyPost:
    if not validate_post_payload(data):
        raise TypeError(
            "data provided to normalize_post is not a standard Bluesky post payload"
        )

    post = {}

    text = data["record"]["text"].encode("utf-8")

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
    post["user_diplay_name"] = data["author"]["displayName"]
    post["user_avatar"] = data["author"]["avatar"]
    post["user_timestamp_utc"], post["user_created_at"] = get_dates(
        data["author"]["createdAt"], locale=locale, source="bluesky"
    )
    post["user_langs"] = data["record"]["langs"]

    # Handle metrics
    post["repost_count"] = data["repostCount"]
    post["reply_count"] = data["replyCount"]
    post["like_count"] = data["likeCount"]
    post["quote_count"] = data["quoteCount"]

    # Handle hashtags, mentions & links from facets
    post["mentioned_user_handles"] = []
    post["mentioned_user_dids"] = []
    hashtags = set()
    links = set()
    links_to_replace = []
    for facet in data["record"].get("facets", []):
        if len(facet["features"]) != 1:
            raise Exception(
                "Unusual facet content for post %s: %s" % (post["url"], facet)
            )

        feat = facet["features"][0]
        if feat["$type"].endswith("#tag"):
            hashtags.add(feat["tag"].strip().lower())

        elif feat["$type"].endswith("#mention"):
            post["mentioned_user_dids"].append(feat["did"])
            handle = text[facet["index"]["byteStart"] + 1 : facet["index"]["byteEnd"]].strip().lower().decode("utf-8")
            post["mentioned_user_handles"].append(handle)

        elif feat["$type"].endswith("#link"):
            links.add(custom_normalize_url(feat["uri"]))
            links_to_replace.append(
                {
                    "uri": feat["uri"].encode("utf-8"),
                    "start": facet["index"]["byteStart"],
                    "end": facet["index"]["byteEnd"],
                }
            )

        else:
            raise Exception("Unusual facet type for post %s: %s" % (post["url"], feat))
    post["hashtags"] = sorted(hashtags)
    post["links"] = sorted(links)

    # Process links domains
    post["domains"] = [
        custom_get_normalized_hostname(
            link, normalize_amp=False, infer_redirection=False
        )
        for link in post["links"]
    ]

    # Rewrite full links within post's text
    for link in sorted(links_to_replace, key=lambda x: x["start"], reverse=True):
        text = text[: link["start"]] + link["uri"] + text[link["end"] :]

    # TODO: add card infos from embed? (type, title, url, image, description
    if "embed" in data:
        pass
        # Sometimes embed.record.embeds ???

    # Handle thread info when applicable
    if "reply" in data["record"]:
        if "parent" in data["record"]["reply"]:
            post["to_user_did"], post["to_post_did"] = parse_post_uri(
                data["record"]["reply"]["parent"]["uri"]
            )
            post["to_post_cid"] = data["record"]["reply"]["parent"]["cid"]
        if "root" in data["record"]["reply"]:
            post["to_root_user_did"], post["to_root_post_did"] = parse_post_uri(
                data["record"]["reply"]["root"]["uri"]
            )
            post["to_root_post_cid"] = data["record"]["reply"]["root"]["cid"]

        # TODO : complete with to_user_handle when did found within mentioned_users, and add to_post_url in those cases?

    # TODO: handle reposts when we can find some in payloads (from user timeline maybe?)

    # TODO: handle quotes & medias
    media_ids = set()
    media_urls = []
    media_files = []
    media_types = []
    media_alt_texts = []
    if "embed" in data["record"]:
        embed = data["record"]["embed"]
        # Quote
        if embed["$type"].endswith(".record"):
            # embed.record uri + cid
            # + from card data.embed.record (replace value by record for full payload)
            pass

        elif embed["$type"].endswith(".recordWithMedia"): # => media and/orquote?
            # embed.media.images alt + image.ref.$link + image.ref.mimeType
            # ou from card data.embed.media.images alt + fullsize
            pass

        # Images
        elif embed["$type"].endswith(".images"):
            for image in embed["images"]:
                media_id = image["image"]["ref"]["$link"]
                if media_id not in media_ids:
                    media_ids.add(media_id)
                    media_type = image["image"]["mimeType"]
                    media_url, media_file = format_media_url_and_file(post["user_did"], media_id, media_type)
                    media_urls.append(media_url)
                    media_types.append(media_type)
                    media_alt_texts.append(image["alt"])
                    media_files.append(media_file)

                # ou from card data.embed.images alt + fullsize

        # Video
        elif embed["$type"].endswith(".video"):
            media_id = embed["video"]["ref"]["$link"]
            if media_id not in media_ids:
                media_ids.add(media_id)
                media_type = embed["video"]["mimeType"]
                media_url, media_file = format_media_url_and_file(post["user_did"], media_id, media_type)
                media_urls.append(media_url)
                media_types.append(media_type)
                # TODO ? store thumbnail in url and playlist in file?
                media_alt_texts.append("")
                media_files.append(media_file)

                # ou from card data.embed.video playlist + thumbnail

        # Link card
        elif embed["$type"].endswith(".external"):
            # example https://bsky.app/profile/bricabraque.bsky.social/post/3lkdnb2gtzk2c
            # embed.external description + thumb.ref.$link/thumb.mimeType + title + uri
            # store as média ? or new card field
            pass

        else:
            raise Exception("Unusual record.embed type for post %s: %s" % (post["url"], embed))

    post["media_urls"] = media_urls
    post["media_types"] = media_types
    post["media_alt_texts"] = media_alt_texts
    post["media_files"] = media_files

    # TODO: handle threadgates?

    # TODO: complete text with medias/quotes when necessary

    post["text"] = text.decode("utf-8")

    return post
