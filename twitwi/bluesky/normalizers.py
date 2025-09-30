from copy import deepcopy
from typing import List, Dict, Union, Optional, Literal, Any, overload

from ural import is_url

from twitwi.exceptions import BlueskyPayloadError
from twitwi.utils import (
    get_collection_time,
    get_dates,
    safe_normalize_url,
    custom_get_normalized_hostname,
)
from twitwi.bluesky.utils import (
    validate_post_payload,
    valid_embed_type,
    format_profile_url,
    format_post_url,
    parse_post_url,
    parse_post_uri,
    format_starterpack_url,
    format_media_url,
)
from twitwi.bluesky.types import BlueskyProfile, BlueskyPartialProfile, BlueskyPost


def normalize_profile(data: Dict, locale: Optional[Any] = None) -> BlueskyProfile:
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
        "url": format_profile_url(data["handle"]),
        "handle": data["handle"],
        "display_name": data.get("displayName"),
        "created_at": created_at,
        "timestamp_utc": timestamp_utc,
        "description": data.get("description"),
        "avatar": data.get("avatar"),
        "posts": data["postsCount"],
        "followers": data["followersCount"],
        "follows": data["followsCount"],
        "lists": associated["lists"],
        "feedgens": associated["feedgens"],
        "starter_packs": associated["starterPacks"],
        "banner": data.get("banner"),
        "pinned_post_uri": pinned_post_uri,
        "collection_time": get_collection_time(),
    }


def normalize_partial_profile(
    data: Dict, locale: Optional[Any] = None
) -> BlueskyPartialProfile:
    associated = data["associated"]

    timestamp_utc, created_at = get_dates(
        data["createdAt"], locale=locale, source="bluesky"
    )

    return {
        "did": data["did"],
        "url": format_profile_url(data["handle"]),
        "handle": data["handle"],
        "display_name": data.get("displayName"),
        "created_at": created_at,
        "timestamp_utc": timestamp_utc,
        "description": data.get("description"),
        "avatar": data.get("avatar"),
        "lists": associated.get("lists"),
        "feedgens": associated.get("feedgens"),
        "starter_packs": associated.get("starterPacks"),
        "collection_time": get_collection_time(),
    }


def prepare_native_gif_as_media(gif_data, user_did, source):
    if "thumb" in gif_data:
        media_cid = gif_data["thumb"]["ref"]["$link"]
        _, thumbnail = format_media_url(user_did, media_cid, "image/jpeg", source)
    else:
        media_cid = ""
        thumbnail = ""

    return {
        "id": media_cid,
        "type": "video/gif",
        "alt": gif_data["title"],
        "url": gif_data["uri"],
        "thumb": thumbnail,
    }


def prepare_image_as_media(image_data):
    if "ref" not in image_data["image"] or "$link" not in image_data["image"]["ref"]:
        image_id = image_data["image"]["cid"]
    else:
        image_id = image_data["image"]["ref"]["$link"]
    return {
        "id": image_id,
        "type": image_data["image"]["mimeType"],
        "alt": image_data["alt"],
    }


def prepare_video_as_media(video_data):
    return {
        "id": video_data["ref"]["$link"],
        "type": video_data["mimeType"],
    }


def process_starterpack_card(embed_data, post):
    # Warning: mutates post

    card = embed_data.get("record", {})
    creator_did, pack_did = parse_post_uri(embed_data["uri"])
    post["card_link"] = format_starterpack_url(
        embed_data.get("creator", {}).get("handle") or creator_did, pack_did
    )
    post["card_title"] = card.get("name", "")
    post["card_description"] = card.get("description", "")
    post["card_thumbnail"] = card.get("thumb", "")
    return post


def process_card_data(embed_data, post):
    # Warning: mutates post

    post["card_link"] = embed_data["uri"]
    post["card_title"] = embed_data.get("title", "")
    post["card_description"] = embed_data.get("description", "")
    post["card_thumbnail"] = embed_data.get("thumb", "")
    return post


def prepare_quote_data(embed_quote, card_data, post, links):
    # Warning: mutates post and links

    post["quoted_cid"] = embed_quote["cid"]
    post["quoted_uri"] = embed_quote["uri"]
    post["quoted_user_did"], post["quoted_did"] = parse_post_uri(
        post["quoted_uri"], post["url"]
    )

    # First store ugly quoted url with user did in case full quote data is missing (recursion > 3 or detached quote)
    # Handling special posts types (only lists for now, for example: https://bsky.app/profile/lanana421.bsky.social/lists/3lxdgjtpqhf2z)
    if "/app.bsky.graph.list/" in post["quoted_uri"]:
        post_splitter = "/lists/"
    else:
        post_splitter = "/post/"
    post["quoted_url"] = format_post_url(
        post["quoted_user_did"], post["quoted_did"], post_splitter=post_splitter
    )

    quoted_data = None
    if card_data:
        if card_data.get("detached", False):
            post["quoted_status"] = "detached"

        else:
            quoted_data = deepcopy(card_data)

    # Grab user handle and cleanup links when no quote data but url in text
    if not quoted_data:
        for link in links:
            if link.startswith("https://bsky.app/profile/") and link.endswith(
                post["quoted_did"]
            ):
                # Take better quoted url with user_handle
                post["quoted_url"] = link
                break

        # Remove quoted link from post links
        if post["quoted_url"] in links:
            links.remove(post["quoted_url"])

        # Extract user handle from url
        if "did:plc:" not in post["quoted_url"]:
            post["quoted_user_handle"], _ = parse_post_url(
                post["quoted_url"], post["url"]
            )

    return (post, quoted_data, links)


def merge_nested_posts(referenced_posts, nested, source):
    for new_post in nested:
        ordered_id = "%s_%s" % (new_post["did"], new_post["user_handle"])
        if ordered_id not in referenced_posts:
            referenced_posts[ordered_id] = new_post
        else:
            old_post = referenced_posts[ordered_id]
            for key in new_post.keys():
                if key not in old_post:
                    old_post[key] = new_post[key]
                elif old_post[key] != new_post[key]:
                    if key == "collected_via":
                        old_post[key] += new_post[key]
                    elif key == "match_query":
                        old_post[key] = old_post[key] or new_post[key]
                    elif key not in ["collection_time"]:
                        raise BlueskyPayloadError(
                            source,
                            "a nested post appearing twice in the same payload has some diverging metadata for key %s: %s / %s"
                            % (key, old_post[key], new_post[key]),
                        )
    return referenced_posts


@overload
def normalize_post(
    payload: Dict,
    locale: Optional[str] = ...,
    extract_referenced_posts: Literal[True] = ...,
    collection_source: Optional[str] = ...,
) -> List[BlueskyPost]: ...


@overload
def normalize_post(
    payload: Dict,
    locale: Optional[str] = ...,
    extract_referenced_posts: Literal[False] = ...,
    collection_source: Optional[str] = ...,
) -> BlueskyPost: ...


def normalize_post(
    payload: Dict,
    locale: Optional[Any] = None,
    extract_referenced_posts: bool = False,
    collection_source: Optional[str] = None,
) -> Union[BlueskyPost, List[BlueskyPost]]:
    """
    Function "normalizing" a post as returned by Bluesky's API in order to
    cleanup and optimize some fields.

    Args:
        payload (dict): post or feed payload json dict from Bluesky API.
        locale (pytz.timezone, optional): Timezone for date conversions.
        extract_referenced_posts (bool, optional): Whether to return, in
            addition to the original post, also the full list of posts
            found in the given payload (including the tree of quoted posts
            as well as the parent and root posts of the thread if the post
            comes as an answer to another one). Defaults
            to `False`.
        collection_source (str, optional): string explaining how the post
            was collected. Defaults to `None`.

    Returns:
        (dict or list): Either a single post dict or a list of post dicts if
            `extract_referenced_posts` was set to `True`.

    """

    if not isinstance(payload, dict):
        raise BlueskyPayloadError(
            "UNKNOWN", f"data provided to normalize_post is not a dictionary: {payload}"
        )

    valid, error = validate_post_payload(payload)
    if not valid:
        raise BlueskyPayloadError(
            payload.get("uri", payload.get("post", {}).get("uri", "UNKNOWN")),
            f"data provided to normalize_post is not a standard Bluesky post or feed payload:\n{error}",
        )

    if "post" in payload:
        data = payload["post"]
        reply_data = payload.get("reply")
        repost_data = payload.get("reason")
    else:
        data = payload
        reply_data = None
        repost_data = None

    if extract_referenced_posts:
        referenced_posts = {}

    if collection_source is None:
        collection_source = data.get("collection_source")

    post = {}

    # Store original text and prepare text for quotes & medias enriched version
    post["original_text"] = data["record"]["text"]
    text = post["original_text"].encode("utf-8")

    # Handle datetime fields
    post["collection_time"] = get_collection_time()
    post["timestamp_utc"], post["local_time"] = get_dates(
        data["record"]["createdAt"], locale=locale, source="bluesky"
    )

    # Handle post/user identifiers
    post["cid"] = data["cid"]
    post["uri"] = data["uri"]
    post["user_did"], post["did"] = parse_post_uri(data["uri"])
    post["user_handle"] = data["author"]["handle"]
    post["user_url"] = format_profile_url(post["user_handle"])
    post["url"] = format_post_url(post["user_handle"], post["did"])

    if post["user_did"] != data["author"]["did"]:
        raise BlueskyPayloadError(
            post["url"],
            "inconsistent user_did between Bluesky post's uri and post's author metadata: %s %s"
            % (data["uri"], data["author"]),
        )

    # Handle user metadata
    post["user_diplay_name"] = data["author"].get("displayName", "")
    post["user_avatar"] = data["author"].get("avatar", "")
    post["user_timestamp_utc"], post["user_created_at"] = get_dates(
        data["author"]["createdAt"], locale=locale, source="bluesky"
    )
    post["user_langs"] = data["record"].get("langs", [])

    if "bridgyOriginalUrl" in data["record"]:
        post["bridgy_original_url"] = data["record"]["bridgyOriginalUrl"]

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
            raise BlueskyPayloadError(
                post["url"],
                "unusual record facet content with more or less than a unique feature: %s"
                % facet,
            )

        feat = facet["features"][0]

        # Hashtags
        if feat["$type"].endswith("#tag") or feat["$type"].endswith("#hashtag"):
            hashtags.add(feat["tag"].strip().lower())

        # Mentions
        elif feat["$type"].endswith("#mention"):
            if feat["did"] not in post["mentioned_user_dids"]:
                post["mentioned_user_dids"].append(feat["did"])

                # Check & fix occasional errored mention positioning
                # example: https://bsky.app/profile/snjcgt.bsky.social/post/3lpmqkkkgp52u
                byteStart = facet["index"]["byteStart"]
                if text[byteStart : byteStart + 1] != b"@":
                    byteStart = text.find(b"@", byteStart)

                handle = (
                    text[
                        byteStart + 1 : facet["index"]["byteEnd"]
                        + byteStart
                        - facet["index"]["byteStart"]
                    ]
                    .strip()
                    .lower()
                    .decode("utf-8")
                )
                post["mentioned_user_handles"].append(handle)

        # Links
        elif feat["$type"].endswith("#link"):
            # Handle native polls
            if "https://poll.blue/" in feat["uri"]:
                if feat["uri"].endswith("/0"):
                    link = safe_normalize_url(feat["uri"])
                    if is_url(link):
                        links.add(link)
                    else:
                        continue
                    text += b" %s" % feat["uri"].encode("utf-8")
                continue

            link = safe_normalize_url(feat["uri"])
            if is_url(link):
                links.add(link)
            else:
                continue
            # Check & fix occasional errored link positioning
            # examples: https://bsky.app/profile/ecrime.ch/post/3lqotmopayr23
            #           https://bsky.app/profile/clustz.com/post/3lqfi7mnto52w
            byteStart = facet["index"]["byteStart"]

            if not text[byteStart : facet["index"]["byteEnd"]].startswith(b"http"):
                new_byteStart = text.find(b"http", byteStart, facet["index"]["byteEnd"])
                if new_byteStart != -1:
                    byteStart = new_byteStart

            links_to_replace.append(
                {
                    "uri": feat["uri"].encode("utf-8"),
                    "start": byteStart,
                    "end": byteStart
                    - facet["index"]["byteStart"]
                    + facet["index"]["byteEnd"],
                }
            )

        elif feat["$type"].endswith("#bold"):
            pass
        elif feat["$type"].endswith("#option"):
            pass
        else:
            raise BlueskyPayloadError(
                post["url"], "unusual record facet feature $type: %s" % feat
            )
    post["hashtags"] = sorted(hashtags)

    # Rewrite full links within post's text
    for link in sorted(links_to_replace, key=lambda x: x["start"], reverse=True):
        if link["start"] < 0:
            text = text + b" " + link["uri"]
        else:
            text = text[: link["start"]] + link["uri"] + text[link["end"] :]

    # Handle thread info when applicable
    # Unfortunately posts' payload only provide at uris for these so we do not have the handles
    # We could sometimes resolve them from the mentionned and quote data but that would not handle most cases
    # Issue opened here to have user handles along: https://github.com/bluesky-social/atproto/issues/3722
    if "reply" in data["record"]:
        if "parent" in data["record"]["reply"]:
            post["to_post_cid"] = data["record"]["reply"]["parent"]["cid"]
            post["to_post_uri"] = data["record"]["reply"]["parent"]["uri"]
            post["to_user_did"], post["to_post_did"] = parse_post_uri(
                post["to_post_uri"], post["url"]
            )
            post["to_post_url"] = format_post_url(
                post["to_user_did"], post["to_post_did"]
            )
        if "root" in data["record"]["reply"]:
            post["to_root_post_cid"] = data["record"]["reply"]["root"]["cid"]
            post["to_root_post_uri"] = data["record"]["reply"]["root"]["uri"]
            post["to_root_user_did"], post["to_root_post_did"] = parse_post_uri(
                post["to_root_post_uri"], post["url"]
            )
            post["to_root_post_url"] = format_post_url(
                post["to_root_user_did"], post["to_root_post_did"]
            )

    # Handle quotes & medias
    media_ids = set()
    post["media_urls"] = []
    post["media_thumbnails"] = []
    post["media_types"] = []
    post["media_alt_texts"] = []
    if "embed" in data["record"]:
        embed = data["record"]["embed"]
        quoted_data = None
        media_data = []
        extra_links = []

        if not valid_embed_type(embed["$type"]):
            raise BlueskyPayloadError(
                post["url"], "unusual record embed $type: %s" % embed
            )

        # Links from cards
        if embed["$type"].endswith(".external"):
            link = embed["external"]["uri"]

            # Handle native gifs as medias
            if link.startswith("https://media.tenor.com/"):
                media_data.append(
                    prepare_native_gif_as_media(
                        embed["external"], post["user_did"], post["url"]
                    )
                )

            # Extra card links sometimes missing from facets & text due to manual action in post form
            else:
                extra_links.append(link)
                # Handle link card metadata
                if "embed" in data:
                    post = process_card_data(data["embed"]["external"], post)

        # Images
        if embed["$type"].endswith(".images"):
            media_data.extend([prepare_image_as_media(i) for i in embed["images"]])

        # Video
        if embed["$type"].endswith(".video"):
            media_data.append(prepare_video_as_media(embed["video"]))

        # Quote & Starter-packs
        if embed["$type"].endswith(".record"):
            if "app.bsky.graph.starterpack" in embed["record"]["uri"]:
                post = process_starterpack_card(
                    data.get("embed", {}).get("record"), post
                )
                if post["card_link"]:
                    extra_links.append(post["card_link"])
            else:
                post, quoted_data, links = prepare_quote_data(
                    embed["record"], data.get("embed", {}).get("record"), post, links
                )

        # Quote with medias
        if embed["$type"].endswith(".recordWithMedia"):
            post, quoted_data, links = prepare_quote_data(
                embed["record"]["record"],
                data.get("embed", {}).get("record", {}).get("record"),
                post,
                links,
            )

            # Links from cards
            if embed["media"]["$type"].endswith(".external"):
                link = embed["media"]["external"]["uri"]

                # Handle native gifs as medias
                if link.startswith("https://media.tenor.com/"):
                    media_data.append(
                        prepare_native_gif_as_media(
                            embed["media"]["external"], post["user_did"], post["url"]
                        )
                    )

                # Extra card links sometimes missing from facets & text due to manual action in post form
                else:
                    extra_links = [link] + extra_links
                    # Handle link card metadata
                    if "embed" in data and "media" in data["embed"]["media"]:
                        post = process_card_data(
                            data["embed"]["media"]["external"], post
                        )

            # Images
            elif embed["media"]["$type"].endswith(".images"):
                media_data.extend(
                    [prepare_image_as_media(i) for i in embed["media"]["images"]]
                )

            # Video
            elif embed["media"]["$type"].endswith(".video"):
                media_data.append(prepare_video_as_media(embed["media"]["video"]))

            else:
                raise BlueskyPayloadError(
                    post["url"],
                    "unusual record embed media $type from a recordWithMedia: %s"
                    % embed,
                )

        # Process extra links
        for link in extra_links:
            norm_link = safe_normalize_url(link)
            if norm_link not in links:
                if is_url(norm_link):
                    links.add(norm_link)
                text += b" " + link.encode("utf-8")

        # Process medias
        for media in media_data:
            if media["id"] not in media_ids:
                media_ids.add(media["id"])
                media_type = media["type"]
                if "url" in media:
                    media_url = media["url"]
                    media_thumb = media["thumb"]
                else:
                    media_url, media_thumb = format_media_url(
                        post["user_did"], media["id"], media_type, post["url"]
                    )
                post["media_urls"].append(media_url)
                post["media_thumbnails"].append(media_thumb)
                post["media_types"].append(media_type)
                post["media_alt_texts"].append(media.get("alt", ""))

                # Rewrite post's text to include links to medias within
                text += b" " + (
                    media_thumb
                    if media_type.startswith("video")
                    and not media_type.endswith("/gif")
                    else media_url
                ).encode("utf-8")

        # Process quotes
        if quoted_data and "value" in quoted_data:
            # We're checking on the uri as the cid can be different in some cases,
            # and the uri seems to be unique for each post
            if quoted_data["uri"] != post["quoted_uri"]: 
                raise BlueskyPayloadError(
                    post["url"],
                    "inconsistent quote uri found between record.embed.record.uri & embed.record.uri: %s %s"
                    % (post["quoted_uri"], quoted_data),
                )

            quoted_data["record"] = quoted_data["value"]
            del quoted_data["value"]
            if "embeds" in quoted_data and len(quoted_data["embeds"]):
                if len(quoted_data["embeds"]) != 1:
                    raise BlueskyPayloadError(
                        post["url"],
                        "unusual multiple embeds found within a quoted post: %s"
                        % quoted_data["embeds"],
                    )
                quoted_data["embed"] = quoted_data["embeds"][0]
                del quoted_data["embeds"]

            nested = normalize_post(
                quoted_data,
                locale=locale,
                extract_referenced_posts=True,
                collection_source="quote",
            )
            quoted = nested[-1]
            if extract_referenced_posts:
                referenced_posts = merge_nested_posts(
                    referenced_posts, nested, post["url"]
                )

            # Take better quoted url with user_handle
            post["quoted_url"] = quoted["url"]
            post["quoted_user_handle"] = quoted["user_handle"]
            post["quoted_created_at"] = quoted["local_time"]
            post["quoted_timestamp_utc"] = quoted["timestamp_utc"]

            # Remove quoted link from post links if present in text
            if quoted["url"] in links:
                links.remove(quoted["url"])

            # Rewrite post's text to include quote within (or replace the link to the quote if present)
            quote = (
                "« @%s: %s — %s »"
                % (quoted["user_handle"], quoted["text"], quoted["url"])
            ).encode("utf-8")
            url_lower = quoted["url"].encode("utf-8").lower()
            text_lower = text.lower()
            if url_lower in text_lower:
                url_pos = text_lower.find(url_lower)
                text = text[:url_pos] + quote + text[url_pos + len(quoted["url"]) :]
            else:
                text += b" " + quote

    # Process links domains
    post["links"] = sorted(links)
    post["domains"] = [custom_get_normalized_hostname(link) for link in post["links"]]

    # Handle threadgates (replies rules)
    # WARNING: quoted posts do not seem to include threadgates info
    # Issue opened about it here: https://github.com/bluesky-social/atproto/issues/3716
    if "threadgate" in data:
        post["replies_rules"] = []
        if "allow" in data["threadgate"]["record"]:
            for rule in data["threadgate"]["record"]["allow"]:
                rule_string = (
                    "allow_from_" + rule["$type"].split("#")[1].split("Rule")[0]
                )
                if rule_string.endswith("_list") and "list" in rule:
                    for allowed_list in rule["list"]:
                        post["replies_rules"].append(rule_string + ":" + allowed_list)
                else:
                    post["replies_rules"].append(rule_string)
            if not data["threadgate"]["record"]["allow"]:
                post["replies_rules"].append("disallow")
        (
            post["replies_rules_timestamp_utc"],
            post["replies_rules_created_at"],
        ) = get_dates(
            data["threadgate"]["record"]["createdAt"], locale=locale, source="bluesky"
        )
        post["hidden_replies_uris"] = data["threadgate"]["record"].get(
            "hiddenReplies", []
        )

    # Handle postgates (quotes rules)
    #
    # Users can forbid others to quote a post, but payloads do not seem to
    # include it yet although the API spec documents it:
    # https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/feed/postgate.json
    # Issue opened about it here: https://github.com/bluesky-social/atproto/issues/3712
    #
    # if "postgate" in data:
    #     if "embeddingRules" in data["postgate"]["record"] and data["postgate"]["record"]["embeddingRules"]:
    #         post["quotes_rule"] = "disallow"
    #     post["quotes_rules_timestamp_utc"], post["quotes_rules_created_at"] = get_dates(data["postgate"]["record"]["createdAt"], locale=locale, source="bluesky")
    #     post["detached_quotes_uris"] = data["postgate"]["record"].get("detachedEmbeddingUris", [])

    # Handle reposts when data comes from a feed
    if repost_data:
        if not repost_data["$type"].endswith("reasonRepost"):
            raise BlueskyPayloadError(
                post["url"],
                "unusual reason for including a post within a feed: %s" % repost_data,
            )

        post["repost_by_user_did"] = repost_data["by"]["did"]
        post["repost_by_user_handle"] = repost_data["by"]["handle"]
        post["repost_timestamp_utc"], post["repost_created_at"] = get_dates(
            repost_data["indexedAt"], locale=locale, source="bluesky"
        )

    try:
        post["text"] = text.decode("utf-8")
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            f"Failed to decode post text: {e}\nPost URL: {post['url']}\nOriginal text bytes: {text}"
        )

    if collection_source is not None:
        post["collected_via"] = [collection_source]
    post["match_query"] = collection_source not in ["thread", "quote"]

    if extract_referenced_posts:
        # Handle thread posts when data comes from a feed
        if reply_data:
            if "parent" in reply_data:
                nested = normalize_post(
                    reply_data["parent"],
                    locale=locale,
                    extract_referenced_posts=True,
                    collection_source="thread",
                )
                referenced_posts = merge_nested_posts(
                    referenced_posts, nested, post["url"]
                )

            if "root" in reply_data and (
                "parent" not in reply_data
                or reply_data["parent"]["cid"] != reply_data["root"]["cid"]
            ):
                nested = normalize_post(
                    reply_data["root"],
                    locale=locale,
                    extract_referenced_posts=True,
                    collection_source="thread",
                )
                referenced_posts = merge_nested_posts(
                    referenced_posts, nested, post["url"]
                )

            if "grandparentAuthor" in reply_data:
                # TODO ? Shall we do anything from that?
                pass

        assert referenced_posts is not None
        return [referenced_posts[did] for did in sorted(referenced_posts.keys())] + [
            post
        ]  # type: ignore

    return post  # type: ignore
