# =============================================================================
# Twitwi Exceptions
# =============================================================================
#
# Custom exceptions used by the library.
#


class TwitwiError(Exception):
    pass


class TwitterWrapperMaxAttemptsExceeded(TwitwiError):
    pass


class TwitterPayloadV2IncompleteIncludesError(TwitwiError):
    def __init__(self, kind, key):
        self.kind = kind
        self.key = key
        super().__init__('{!r} ({})'.format(key, kind))
