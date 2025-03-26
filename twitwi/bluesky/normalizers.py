from typing import Dict

from twitwi.bluesky.types import BlueskyProfile


def normalize_profile(data: Dict) -> BlueskyProfile:
    return {
        "did": data["did"],
        "handle": data["handle"],
        "display_name": data["displayName"],
    }
