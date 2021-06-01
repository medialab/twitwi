# =============================================================================
# Twitwi Formatters
# =============================================================================
#
# Miscellaneous formatter functions transforming tweets from one format
# to the other.
#
from twitwi.constants import (
    TWEET_FIELDS,
    TWEET_BOOLEAN_FIELDS,
    TWEET_PLURAL_FIELDS,
    USER_FIELDS,
    USER_BOOLEAN_FIELDS,
    USER_PLURAL_FIELDS
)


def find_longest(domains, already_found):
    if len(domains) == 0:
        return None
    candidate = max(domains, key=len)
    if len(already_found) == 0:
        return candidate
    for found in already_found:
        if candidate in found:
            domains.remove(candidate)
            candidate = find_longest(domains, already_found)
    return candidate


def n_longest_domains(domains, nb_results):
    candidates = set(domains)
    results = set()
    for i in range(nb_results):
        new_longest = find_longest(candidates, results)
        if new_longest is not None:
            results.add(new_longest)
            candidates.remove(new_longest)
    return sorted(results, key=len, reverse=True)


def make_transform_into_csv_dict(plural_fields, boolean_fields):

    def transform_into_csv_dict(item, item_id=None, plural_separator='|'):
        if item_id is not None:
            item['id'] = item_id

        item['links'] = item.get('proper_links', item.get('links', []))
        item['domains'] = n_longest_domains(item['domains'], len(item['links'])) if "domains" in item else []
        for plural_field in plural_fields:
            item[plural_field] = plural_separator.join(item.get(plural_field, []))

        for boolean_field in boolean_fields:
            item[boolean_field] = int(item[boolean_field]) if boolean_field in item else ''

    return transform_into_csv_dict


def make_format_as_csv_row(fields, plural_fields, boolean_fields):

    def format_field_for_csv(field, item, item_id=None, plural_separator='|'):

        if field == 'id' and item_id is not None:
            return item_id

        # NOTE: this is hardly the most performant way to proceed by I am lazy...
        if field in plural_fields:
            v = item.get(field, [])

            if field == 'links':
                v = item.get('proper_links', v)

            if field == 'domains':
                v = n_longest_domains(v, len(item.get('links', [])))

            return plural_separator.join(v)

        if field in boolean_fields:
            return int(item[field]) if field in item else ''

        return item.get(field, '')

    def format_item_as_csv_row(item, item_id=None, plural_separator='|'):
        return [
            format_field_for_csv(
                field,
                item,
                item_id=item_id,
                plural_separator=plural_separator
            )
            for field in fields
        ]

    return format_item_as_csv_row


transform_tweet_into_csv_dict = make_transform_into_csv_dict(
    TWEET_PLURAL_FIELDS,
    TWEET_BOOLEAN_FIELDS
)

format_tweet_as_csv_row = make_format_as_csv_row(
    TWEET_FIELDS,
    TWEET_PLURAL_FIELDS,
    TWEET_BOOLEAN_FIELDS
)

transform_user_into_csv_dict = make_transform_into_csv_dict(
    USER_PLURAL_FIELDS,
    USER_BOOLEAN_FIELDS
)

format_user_as_csv_row = make_format_as_csv_row(
    USER_FIELDS,
    USER_PLURAL_FIELDS,
    USER_BOOLEAN_FIELDS
)

__all__ = [
    'transform_tweet_into_csv_dict',
    'format_tweet_as_csv_row',
    'transform_user_into_csv_dict',
    'format_user_as_csv_row'
]
