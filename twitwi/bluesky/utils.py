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


def validate_post_payload(post):
    if not isinstance(post, dict):
        return False

    if not all(key in post for key in valid_post_keys):
        return False

    if not isinstance(post["record"], dict):
        return False

    if not all(key in post["record"] for key in valid_record_keys):
        return False

    if post["record"].get("$type") != "app.bsky.feed.post":
        return False

    if not isinstance(post["author"], dict):
        return False

    if not all(key in post["author"] for key in valid_author_keys):
        return False

    return True
