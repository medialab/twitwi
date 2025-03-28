def validate_post_payload(post):
    if not isinstance(post, dict):
        return False

    if not all(
        key in post
        for key in [
            "cid",
            "uri",
            "author",
            "record",
            "replyCount",
            "repostCount",
            "likeCount",
            "quoteCount",
        ]
    ):
        return False

    if not isinstance(post["record"], dict):
        return False

    if not all(
        key in post["record"] for key in ["$type", "createdAt", "langs", "text"]
    ):
        return False

    if post["record"].get("$type") != "app.bsky.feed.post":
        return False

    if not isinstance(post["author"], dict):
        return False

    if not all(
        key in post["author"]
        for key in ["did", "handle", "displayName", "avatar", "createdAt"]
    ):
        return False

    # TODO: test all valid $type in embed and associated elements

    return True
