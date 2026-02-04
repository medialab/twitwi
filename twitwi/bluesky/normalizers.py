from copy import deepcopy
from typing import List, Dict, Union, Optional, Literal, Any, overload, Tuple, Set

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
    validate_partial_post_payload,
    valid_embed_type,
    format_profile_url,
    format_post_url,
    format_post_uri,
    parse_post_url,
    parse_post_uri,
    format_starterpack_url,
    format_media_url,
    format_external_embed_thumbnail_url,
)
from twitwi.bluesky.types import BlueskyProfile, BlueskyPartialProfile, BlueskyPost, BlueskyPartialPost


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
    if "uri" in embed_data:
        creator_did, pack_did = parse_post_uri(embed_data["uri"])
        post["card_link"] = format_starterpack_url(
            embed_data.get("creator", {}).get("handle") or creator_did, pack_did
        )
    if card:
        post["card_title"] = card.get("name", "")
        post["card_description"] = card.get("description", "")
        post["card_thumbnail"] = card.get("thumb", "")


# Warning: mutates post
def process_card_data(embed_data, post):
    post["card_link"] = embed_data["uri"]
    post["card_title"] = embed_data.get("title", "")
    post["card_description"] = embed_data.get("description", "")
    post["card_thumbnail"] = format_external_embed_thumbnail_url(
        embed_data.get("thumb", {}).get("ref", {}).get("$link", ""), post["user_did"]
    )


# Warning: mutates post and links
def prepare_quote_data(embed_quote, card_data, post, links):
    quoted_data = None

    post["quoted_cid"] = embed_quote["cid"]
    post["quoted_uri"] = embed_quote["uri"]
    # Sometimes quoted post is not found, even if uri and cid are given
    # example: https://bsky.app/profile/takobiotech.masto.bike.ap.brid.gy/post/3lc6r7nzil6m2
    if card_data and card_data.get("notFound"):
        post["quoted_status"] = "notFound"
    else:
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

        if card_data:
            if card_data.get("detached"):
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

    return quoted_data


# Warning: mutates referenced_posts
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

# Handle hashtags, mentions & links from facets
# Warning: mutates post
def process_post_facets(facets: List[Dict], post: Dict, text: str) -> Tuple[str, Set[str]]:
    post["mentioned_user_handles"] = []
    post["mentioned_user_dids"] = []
    hashtags = set()
    links = set()
    links_to_replace = []
    for facet in facets:
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
                byteEnd = facet["index"]["byteEnd"]
                if text[byteStart : byteStart + 1] != b"@":
                    byteStart = text.find(b"@", byteStart)
                # in some cases, the errored positioning is before the position given
                # example: https://bsky.app/profile/springer.springernature.com/post/3lovyad4nt324
                if byteStart == -1 or byteStart > byteEnd:
                    # When decrementing byteStart, we also decrement byteEnd (see below)
                    # shifting the slice to extract the mention correctly
                    byteStart = facet["index"]["byteStart"] - 1
                    # to extend the size of the mention, which is somehow 1 char too short because of the '@'
                    byteEnd += 1

                handle = (
                    text[
                        byteStart + 1 : byteEnd
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
            byteEnd = facet["index"]["byteEnd"]

            if not text[byteStart:byteEnd].startswith(b"http"):
                new_byteStart = text.find(b"http", byteStart, byteEnd)

                # means that the link is shifted, like on this post:
                # https://bsky.app/profile/ecrime.ch/post/3lqotmopayr23
                if new_byteStart != -1:
                    byteStart = new_byteStart

                    # Find the index of the first space character after byteStart in case the link is a personalized one
                    # but still with the link in it (somehow existing in some posts, such as this one:
                    # https://bsky.app/profile/did:plc:rkphrshyfiqe4n2hz5vj56ig/post/3ltmljz5blca2)
                    # In this case, we don't want to touch the position of the link given in the payload
                    byteEnd = min(
                        byteStart
                        - facet["index"]["byteStart"]
                        + facet["index"]["byteEnd"],
                        len(post["original_text"].encode("utf-8")),
                    )
                    for i in range(byteStart, byteEnd):
                        if chr(text[i]).isspace():
                            byteStart = facet["index"]["byteStart"]
                    byteEnd = (
                        byteStart
                        - facet["index"]["byteStart"]
                        + facet["index"]["byteEnd"]
                    )

                # means that the link is a "personalized" one like on this post:
                # https://bsky.app/profile/newyork.activitypub.awakari.com.ap.brid.gy/post/3ln33tx7bpdu2
                else:
                    # we're looking for a link which could be valid if we add "https://" at the beginning,
                    # as in some cases the "http(s)://" part is missing in the post text
                    for starting in range(byteEnd - byteStart):
                        try:
                            if is_url(
                                "https://"
                                + text[
                                    byteStart + starting : byteEnd + starting
                                ].decode("utf-8")
                            ):
                                byteStart += starting
                                break
                        except UnicodeDecodeError:
                            pass
                    # If we did not find any valid link, we just keep the original position as it is
                    # meaning that we have a personalized link like in the example above

                    # Extend byteEnd to the right until we find a valid utf-8 ending,
                    # as in some cases the link is longer than the position given in the payload
                    # and it gets cut in the middle of a utf-8 char, leading to UnicodeDecodeError
                    # example: https://bsky.app/profile/radiogaspesie.bsky.social/post/3lmkzhvhtta22
                    while byteEnd <= len(post["original_text"].encode("utf-8")):
                        try:
                            text[byteStart:byteEnd].decode("utf-8")
                            break
                        except UnicodeDecodeError:
                            byteEnd += 1
                            continue

                    if byteEnd > len(post["original_text"].encode("utf-8")):
                        byteEnd = facet["index"]["byteEnd"]

                    byteEnd += byteStart - facet["index"]["byteStart"]

            # In some cases, the link is completely wrong in the post text,
            # like in this post: https://bsky.app/profile/sudetsoleil.bsky.social/post/3ljf3h74wee2m
            # So we chose to not replace anything in the text in this case
            try:
                text[byteStart:byteEnd].decode("utf-8")
                links_to_replace.append(
                    {
                        "uri": feat["uri"].encode("utf-8"),
                        "start": byteStart,
                        "end": byteEnd,
                    }
                )
            except UnicodeDecodeError:
                pass
                # raise UnicodeDecodeError(e.encoding, e.object, e.start, e.end, f"{e.reason} in post {post['url']}.\nText to decode: {text}\nSlice of text to decode: {text[e.start:e.end]}")

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

    return text, links

# Handle thread info when applicable
# Warning: mutates post
def process_post_thread_info(reply_data: Dict, post: Dict):
    if "parent" in reply_data:
        post["to_post_cid"] = reply_data["parent"]["cid"]
        post["to_post_uri"] = reply_data["parent"]["uri"]
        post["to_user_did"], post["to_post_did"] = parse_post_uri(
            post["to_post_uri"], post["url"]
        )
        post["to_post_url"] = format_post_url(
            post["to_user_did"], post["to_post_did"]
        )
    if "root" in reply_data:
        post["to_root_post_cid"] = reply_data["root"]["cid"]
        post["to_root_post_uri"] = reply_data["root"]["uri"]
        post["to_root_user_did"], post["to_root_post_did"] = parse_post_uri(
            post["to_root_post_uri"], post["url"]
        )
        post["to_root_post_url"] = format_post_url(
            post["to_root_user_did"], post["to_root_post_did"]
        )


# Handle quotes & medias
# Warning: mutates post, links and referenced_posts
def process_links_from_card(record: Dict, post: Dict, links: Set[str], text: str, locale: Optional[Any], extract_referenced_posts: bool, referenced_posts: Dict, data: Dict = {}) -> str:
    media_ids = set()
    embed = record["embed"]
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
            # Warning: mutates post
            process_card_data(embed["external"], post)

    # Images
    if embed["$type"].endswith(".images"):
        media_data.extend([prepare_image_as_media(i) for i in embed["images"]])

    # Video
    if embed["$type"].endswith(".video"):
        media_data.append(prepare_video_as_media(embed["video"]))

    # Quote & Starter-packs
    if embed["$type"].endswith(".record"):
        if "app.bsky.graph.starterpack" in embed["record"]["uri"]:
            # Warning: mutates post
            process_starterpack_card(
                data.get("embed", {}).get("record", {}), post
            )
            if post.get("card_link"):
                extra_links.append(post["card_link"])
        else:
            # Warning: mutates post and links
            quoted_data = prepare_quote_data(
                embed["record"], data.get("embed", {}).get("record", {}), post, links
            )

    # Quote with medias
    if embed["$type"].endswith(".recordWithMedia"):
        # Warning: mutates post and links
        quoted_data = prepare_quote_data(
            embed["record"]["record"],
            data.get("embed", {}).get("record", {}).get("record", {}),
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
                    # Warning: mutates post
                    process_card_data(
                        embed["media"]["external"], post
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
            # Warning: mutates referenced_posts
            merge_nested_posts(
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

    return text


# Process links domains
# Warning: mutates post
def process_links_domains(post:Dict, links: Set[str]):
    post["links"] = sorted(links)
    post["domains"] = [custom_get_normalized_hostname(link) for link in post["links"]]


# Finalize text field
# Warning: mutates post
def finalize_post_text(text: str, post: Dict):
    try:
        post["text"] = text.decode("utf-8")
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            e.encoding,
            e.object,
            e.start,
            e.end,
            f"{e.reason} in post {post['url']}.\nText to decode: {text}\nSlice of text to decode: {text[e.start : e.end]}",
        )


# Collection source & match query
# Warning: mutates post
def process_collection_source_and_match_query(post: Dict, collection_source: Optional[str]):
    if collection_source is not None:
        post["collected_via"] = [collection_source]
    post["match_query"] = collection_source not in ["thread", "quote"]


# Handle thread posts when data comes from a feed
# Warning: mutates referenced_posts
def process_thread_posts_from_feed(reply_data: Dict, post: Dict, locale: Optional[Any], extract_referenced_posts: bool, referenced_posts: Dict):
    if "parent" in reply_data:
        nested = normalize_post(
            reply_data["parent"],
            locale=locale,
            extract_referenced_posts=True,
            collection_source="thread",
        )
        # Warning: mutates referenced_posts
        merge_nested_posts(
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
        # Warning: mutates referenced_posts
        merge_nested_posts(
            referenced_posts, nested, post["url"]
        )

    if "grandparentAuthor" in reply_data:
        # TODO ? Shall we do anything from that?
        pass



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
    post["indexed_at_utc"] = data["indexedAt"]

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
    post["user_display_name"] = data["author"].get("displayName", "")
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
    # When a post cites another, the cited post doesn't have the bookmarkCount field
    post["bookmark_count"] = data.get("bookmarkCount")

    # Handle hashtags, mentions & links from facets
    # Warning: mutates post
    text, links = process_post_facets(
        data["record"].get("facets", []), post, text
    )

    # Handle thread info when applicable
    # Unfortunately posts' payload only provide at uris for these so we do not have the handles
    # We could sometimes resolve them from the mentionned and quote data but that would not handle most cases
    # Issue opened here to have user handles along: https://github.com/bluesky-social/atproto/issues/3722
    if "reply" in data["record"]:
        # Warning: mutates post
        process_post_thread_info(data["record"]["reply"], post)

    # Handle quotes & medias
    post["media_urls"] = []
    post["media_thumbnails"] = []
    post["media_types"] = []
    post["media_alt_texts"] = []
    if "embed" in data["record"]:
        # Warning: mutates post, links and referenced_posts
        text = process_links_from_card(
            data["record"],
            post,
            links,
            text,
            locale,
            extract_referenced_posts,
            referenced_posts,
            data,
        )


    # Process links domains
    # Warning: mutates post
    process_links_domains(post, links)


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

    # Finalize text field
    # Warning: mutates post
    finalize_post_text(text, post)


    # Collection source & match query handling
    # Warning: mutates post
    process_collection_source_and_match_query(post, collection_source)


    if extract_referenced_posts:
        # Handle thread posts when data comes from a feed
        if reply_data:
            # Warning: mutates referenced_posts
            process_thread_posts_from_feed(
                reply_data, post, locale, extract_referenced_posts, referenced_posts
            )

        assert referenced_posts is not None
        return [referenced_posts[did] for did in sorted(referenced_posts.keys())] + [
            post
        ]  # type: ignore

    return post  # type: ignore



def normalize_partial_post(
    payload: Dict,
    locale: Optional[Any] = None,
    collection_source: Optional[str] = None,
) -> BlueskyPartialPost:
    """
    Function "normalizing" a partial payload post as returned by Bluesky's Firehose in order to
    cleanup and optimize some fields.

    Args:
        payload (dict): partial post or feed payload json dict from Bluesky Firehose.
        locale (pytz.timezone, optional): Timezone for date conversions.
        collection_source (str, optional): string explaining how the post
            was collected. Source application of the payload, either `firehose` or `tap`,
            which is experimental for now. Defaults to `None`.

    Returns:
        (dict or list): Either a single partial post dict or a list of partial post dicts if
            `extract_referenced_posts` was set to `True`.

    """

    if not isinstance(payload, dict):
        raise BlueskyPayloadError(
            "UNKNOWN", f"data provided to normalize_partial_post is not a dictionary: {payload}"
        )

    if collection_source not in ["firehose", "tap", "unit_test"]:
        raise ValueError(f"collection_source must be either 'firehose' or 'tap', got: {collection_source}")

    if collection_source == "firehose":
        post_field = "commit"
    else:  # tap
        post_field = "record"

    valid, error = validate_partial_post_payload(payload, collection_source=collection_source)

    if not valid:
        uri = format_post_uri(
            payload.get("did", payload.get(post_field, {}).get("did", "UNKNOWN")),
            payload.get(post_field, {}).get("rkey", "UNKNOWN"),
        )
        raise BlueskyPayloadError(
            uri,
            f"data provided to normalize_partial_post is not a standard Bluesky post or feed payload:\n{error}",
        )

    if "post" in payload:
        data = payload["post"]
    else:
        data = payload

    referenced_posts = {}

    post = {}

    post["collection_source"] = collection_source

    # Store original text and prepare text for quotes & medias enriched version
    post["original_text"] = data[post_field]["record"]["text"]
    text = post["original_text"].encode("utf-8")

    # Handle datetime fields
    post["collection_time"] = get_collection_time()
    post["timestamp_utc"], post["local_time"] = get_dates(
        data[post_field]["record"]["createdAt"], locale=locale, source="bluesky"
    )
    post["firehose_timestamp_us"] = data["time_us"] if collection_source == "firehose" else None

    # Handle post/user identifiers
    post["cid"] = data[post_field]["cid"]
    post["user_did"] = data.get("did", payload.get(post_field, {}).get("did"))
    post["did"] = data[post_field]["rkey"]
    post["uri"] = format_post_uri(post["user_did"], post["did"])

    post["user_url"] = format_profile_url(post["user_did"])
    post["url"] = format_post_url(post["user_did"], post["did"])

    # Handle user metadata
    post["user_langs"] = data[post_field]["record"].get("langs", [])

    if "bridgyOriginalUrl" in data[post_field]["record"]:
        post["bridgy_original_url"] = data[post_field]["record"]["bridgyOriginalUrl"]

    # Handle hashtags, mentions & links from facets
    # Warning: mutates post
    text, links = process_post_facets(
        data[post_field]["record"].get("facets", []), post, text
    )

    # Handle thread info when applicable
    # Unfortunately posts' payload only provide at uris for these so we do not have the handles
    # We could sometimes resolve them from the mentionned and quote data but that would not handle most cases
    # Issue opened here to have user handles along: https://github.com/bluesky-social/atproto/issues/3722
    if "reply" in data[post_field]["record"]:
        # Warning: mutates post
        process_post_thread_info(data[post_field]["record"]["reply"], post)

    # Handle quotes & medias
    post["media_urls"] = []
    post["media_thumbnails"] = []
    post["media_types"] = []
    post["media_alt_texts"] = []
    if "embed" in data[post_field]["record"]:
        # Warning: mutates post, links and referenced_posts
        text = process_links_from_card(
            data[post_field]["record"],
            post,
            links,
            text,
            locale,
            False,
            referenced_posts,
        )


    # Process links domains
    # Warning: mutates post
    process_links_domains(post, links)


    # Finalize text field
    # Warning: mutates post
    finalize_post_text(text, post)


    # Collection source & match query handling
    # Warning: mutates post
    process_collection_source_and_match_query(post, collection_source)


    return post  # type: ignore
