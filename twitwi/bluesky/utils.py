import re

from twitwi.exceptions import BlueskyPayloadError


valid_post_keys = [
    "cid",
    "uri",
    "author",
    "record",
    "replyCount",
    "repostCount",
    "likeCount",
    "quoteCount",
]

valid_record_keys = ["$type", "createdAt", "text"]


valid_author_keys = ["did", "handle", "displayName", "avatar", "createdAt"]


def validate_post_payload(data):
    post = data.get("post", data)

    for key in valid_post_keys:
        if key not in post:
            return False, f"key {key} is missing from payload: {post}"

    if not isinstance(post["record"], dict):
        return False, "payload's record is not a dictionary: %s" % post["record"]

    for key in valid_record_keys:
        if key not in post["record"]:
            return False, "key %s is missing from payload's record: %s" % (
                key,
                post["record"],
            )

    if post["record"].get("$type") != "app.bsky.feed.post":
        return False, "payload's record $type is not a post: %s" % post["record"].get(
            "$type"
        )

    if not isinstance(post["author"], dict):
        return False, "payload's author is not a dictionary: %s" % post["author"]

    for key in valid_author_keys:
        if key not in post["author"]:
            return False, "key %s is missing from payload's author: %s" % (
                key,
                post["author"],
            )

    return True, None


re_embed_types = re.compile(r"\.(record|recordWithMedia|images|video|external)$")


def valid_embed_type(embed_type):
    return re_embed_types.search(embed_type)


def format_profile_url(user_handle_or_did):
    return f"https://bsky.app/profile/{user_handle_or_did}"


def format_post_url(user_handle_or_did, post_did):
    return f"https://bsky.app/profile/{user_handle_or_did}/post/{post_did}"


def parse_post_url(url, source):
    """Returns a tuple of (author_handle/did, post_did) from an https://bsky.app post URL"""

    if not url.startswith("https://bsky.app/profile/") and "/post/" not in url:
        raise BlueskyPayloadError(source, f"{url} is not a usual Bluesky post url")
    return url[25:].split("/post/")


def parse_post_uri(uri, source=None):
    """Returns a tuple of (author_did, post_did) from an at:// post URI"""

    if not uri.startswith("at://") and "/app.bsky.feed.post/" not in uri:
        raise BlueskyPayloadError(
            source or uri, f"{uri} is not a usual Bluesky post uri"
        )
    return uri[5:].split("/app.bsky.feed.post/")


def format_media_url(user_did, media_cid, mime_type, source):
    media_type = mime_type.split("/")[1]
    if mime_type.startswith("image"):
        media_url = f"https://cdn.bsky.app/img/feed_fullsize/plain/{user_did}/{media_cid}@{media_type}"
        media_thumb = f"https://cdn.bsky.app/img/feed_thumbnail/plain/{user_did}/{media_cid}@{media_type}"
    elif mime_type.startswith("video"):
        media_url = f"https://video.bsky.app/watch/{user_did}/{media_cid}/playlist.m3u8"
        media_thumb = (
            f"https://video.bsky.app/watch/{user_did}/{media_cid}/thumbnail.jpg"
        )
    else:
        raise BlueskyPayloadError(source, f"{mime_type} is an usual media mimeType")
    return media_url, media_thumb
