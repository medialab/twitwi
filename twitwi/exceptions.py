# =============================================================================
# Twitwi Exceptions
# =============================================================================
#
# Custom exceptions used by the library.
#


class TwitwiError(Exception):
    pass


class TwitterPayloadV2IncompleteIncludesError(TwitwiError):
    def __init__(self, kind, key):
        self.kind = kind
        self.key = key
        super().__init__("{!r} ({})".format(key, kind))


class BlueskyPayloadError(TwitwiError):
    def __init__(self, source, message):
        self.source = source
        self.message = message
        super().__init__(f"Error while processing Bluesky post {source}:\n{message}")
