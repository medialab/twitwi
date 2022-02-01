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
