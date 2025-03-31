import re
from copy import deepcopy
from typing import List, Dict, Union, Optional

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


# TODO: give more debugging info on source in all Exception raised

re_embed_types = re.compile(r"\.(record|recordWithMedia|images|video|external)$")


def normalize_post(
    data: Dict,
    locale: Optional[str] = None,
    extract_referenced_posts: bool = False,
    collection_source=None,
) -> Union[BlueskyPost, List[BlueskyPost]]:
    """
    Function "normalizing" a post as returned by Bluesky's API in order to
    cleanup and optimize some fields.

    Args:
        data (dict): Post json dict from Bluesky API.
        locale (pytz.timezone, optional): Timezone for date conversions.
        extract_referenced_posts (bool, optional): Whether to return only
            the original post or the full list of posts found in the given
            payload (including quoted and reposted posts). Defaults
            to `False`.
        collection_source (str, optional): string explaining how the post
            was collected. Defaults to `None`.

    Returns:
        (dict or list): Either a single post dict or a list of post dicts if
            `extract_referenced_posts` was set to `True`.

    """

    if not validate_post_payload(data):
        raise TypeError(
            "data provided to normalize_post is not a standard Bluesky post payload"
        )

    post = {}

    if extract_referenced_posts:
        referenced_posts = []

    if collection_source is None:
        collection_source = data.get("collection_source")

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
    post["user_langs"] = data["record"].get("langs", [])

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
            # TODO ? check user mentioned multiple times and keep only once? ex https://bsky.app/profile/bikopie.bsky.social/post/3llkleq3lyk2d
            post["mentioned_user_dids"].append(feat["did"])
            handle = (
                text[facet["index"]["byteStart"] + 1 : facet["index"]["byteEnd"]]
                .strip()
                .lower()
                .decode("utf-8")
            )
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

    # Rewrite full links within post's text
    for link in sorted(links_to_replace, key=lambda x: x["start"], reverse=True):
        text = text[: link["start"]] + link["uri"] + text[link["end"] :]

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

        # TODO : complete with to_user_handle when did found within mentioned_users, and add to_post_url in those cases? Add replied to mentionned?

    # TODO: handle reposts when we can find some in payloads (from user timeline maybe?)

    # Handle quotes & medias
    media_ids = set()
    media_urls = []
    media_files = []
    media_types = []
    media_alt_texts = []
    if "embed" in data["record"]:
        embed = data["record"]["embed"]
        quoted_data = None
        media_data = []
        extra_links = []

        if not re_embed_types.search(embed["$type"]):
            raise Exception(
                "Unusual record.embed type for post %s: %s" % (post["url"], embed)
            )

        # Link from cards (includes native gif links and links sometimes not already present within facets & text due to manual action in post form)
        if embed["$type"].endswith(".external"):
            extra_links.append(embed["external"]["uri"])

            # example of gif : https://bsky.app/profile/shiseptiana.bsky.social/post/3lkbalaxeys2v https://bsky.app/profile/nicholehiltz.bsky.social/post/3llmkipfkc22q
            # -> seems like gif embedded always come from media.tenor.com, handle these separately as media instead of links?
            # embed.external title(=alt) + uri + thumb.ref.$link/thumb.mimeType (=thumb)
            # embed.external description + thumb.ref.$link/thumb.mimeType + title + uri
            # store as média ? or new card field

        # Images
        if embed["$type"].endswith(".images"):
            media_data.extend(
                [
                    {
                        "id": i["image"]["ref"]["$link"],
                        "type": i["image"]["mimeType"],
                        "alt": i["alt"],
                    }
                    for i in embed["images"]
                ]
            )

        # Video
        if embed["$type"].endswith(".video"):
            media_data.append(
                {
                    "id": embed["video"]["ref"]["$link"],
                    "type": embed["video"]["mimeType"],
                }
            )

        # Quote
        if embed["$type"].endswith(".record"):
            post["quoted_user_did"], post["quoted_did"] = parse_post_uri(
                embed["record"]["uri"]
            )
            post["quoted_cid"] = embed["record"]["cid"]

            if "embed" in data:
                quoted_data = deepcopy(data["embed"]["record"])

        # Quote with medias
        if embed["$type"].endswith(".recordWithMedia"):
            # example https://bsky.app/profile/pecqueuxanthony.bsky.social/post/3lkizm6uvhc2b
            # embed.media.images alt + image.ref.$link + image.ref.mimeType
            # ou from card data.embed.media.images alt + fullsize
            post["quoted_user_did"], post["quoted_did"] = parse_post_uri(
                embed["record"]["record"]["uri"]
            )
            post["quoted_cid"] = embed["record"]["record"]["cid"]

            if "embed" in data:
                quoted_data = deepcopy(data["embed"]["record"]["record"])

            if embed["media"]["$type"].endswith(".images"):
                media_data.extend(
                    [
                        {
                            "id": i["image"]["ref"]["$link"],
                            "type": i["image"]["mimeType"],
                            "alt": i["alt"],
                        }
                        for i in embed["media"]["images"]
                    ]
                )

            elif embed["media"]["$type"].endswith(".video"):
                media_data.append(
                    {
                        "id": embed["media"]["video"]["ref"]["$link"],
                        "type": embed["media"]["video"]["mimeType"],
                    }
                )

            elif embed["media"]["$type"].endswith(".external"):
                extra_links = [embed["media"]["external"]["uri"]] + extra_links

            # TODO : recordWithMedia

            else:
                raise Exception(
                    "Encountered unhandled recordWithMedia type: %s"
                    % embed["media"]["$type"]
                )

        # Process extra links
        for link in extra_links:
            norm_link = custom_normalize_url(link)
            if norm_link not in links:
                links.add(norm_link)
                text += b" " + link.encode("utf-8")

        # Process medias
        for media in media_data:
            if media["id"] not in media_ids:
                media_ids.add(media["id"])
                media_type = media["type"]
                media_url, media_file = format_media_url_and_file(
                    post["user_did"], media["id"], media_type
                )
                media_urls.append(media_url)
                media_types.append(media_type)
                media_alt_texts.append(media.get("alt", ""))
                media_files.append(media_file)
                # TODO ? store videos thumbnail in url and playlist in file?

            # ou from card data.embed.images alt + fullsize
            # ou from card data.embed.video playlist + thumbnail

        # Process quotes
        if quoted_data:
            if quoted_data["cid"] != post["quoted_cid"]:
                raise Exception(
                    "Inconsistent quote cid found between record.embed.record.cid & embed.record.cid"
                )

            quoted_data["record"] = quoted_data["value"]
            del quoted_data["value"]
            if "embeds" in quoted_data and len(quoted_data["embeds"]):
                if len(quoted_data["embeds"]) != 1:
                    raise Exception("Unusual multiple embeds found within a post!")
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
                referenced_posts.extend(nested)

            post["quoted_user_handle"] = quoted["user_handle"]
            post["quoted_timestamp_utc"] = quoted["timestamp_utc"]
            # TODO : need to rewrite quoted url when present (from manual quotes) like we use to do in twitter, ex: https://bsky.app/profile/boogheta.bsky.social/post/3llon4g5lks2h
            text += (
                " « @%s: %s — %s »"
                % (quoted["user_handle"], quoted["text"], quoted["url"])
            ).encode("utf-8")

            # TODO ? add quoted_user as mentionned ? add quoted url as link ? add quoted hashtags to hashtags ? add quoted links as links ?

    # TODO: add card infos from embed? (type, title, url, image, description
    if "embed" in data:
        pass

    # Process links domains
    # TODO? same code as Tw, actually subdomains returned, more practical, but inaccurate with naming, change it?
    post["links"] = sorted(links)
    post["domains"] = [
        custom_get_normalized_hostname(
            link, normalize_amp=False, infer_redirection=False
        )
        for link in post["links"]
    ]

    post["media_urls"] = media_urls
    post["media_types"] = media_types
    post["media_alt_texts"] = media_alt_texts
    post["media_files"] = media_files
    # TODO ? add media_urls as link ?

    # TODO: handle threadgates?

    # TODO: complete text with medias when necessary

    post["text"] = text.decode("utf-8")

    if collection_source is not None:
        post["collected_via"] = [collection_source]
    post["match_query"] = collection_source not in ["thread", "quote"]

    if extract_referenced_posts:
        return referenced_posts + [post]

    return post
