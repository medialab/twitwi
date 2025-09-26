from twitwi.formatters import make_transform_into_csv_dict, make_format_as_csv_row
from twitwi.bluesky.constants import (
    PROFILE_FIELDS,
    PARTIAL_PROFILE_FIELDS,
    POST_FIELDS,
    POST_PLURAL_FIELDS,
    POST_BOOLEAN_FIELDS,
)


transform_post_into_csv_dict = make_transform_into_csv_dict(
    POST_PLURAL_FIELDS, POST_BOOLEAN_FIELDS
)

format_post_as_csv_row = make_format_as_csv_row(
    POST_FIELDS, POST_PLURAL_FIELDS, POST_BOOLEAN_FIELDS
)


transform_profile_into_csv_dict = make_transform_into_csv_dict([], [])

format_profile_as_csv_row = make_format_as_csv_row(PROFILE_FIELDS, [], [])

transform_partial_profile_into_csv_dict = make_transform_into_csv_dict([], [])

format_partial_profile_as_csv_row = make_format_as_csv_row(
    PARTIAL_PROFILE_FIELDS, [], []
)


__all__ = [
    "transform_post_into_csv_dict",
    "format_post_as_csv_row",
    "transform_profile_into_csv_dict",
    "format_profile_as_csv_row",
    "transform_partial_profile_into_csv_dict",
    "format_partial_profile_as_csv_row",
]
