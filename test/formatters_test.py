# =============================================================================
# Twitwi Formatters Unit Tests
# =============================================================================
import ndjson
import csv
from io import StringIO
from test.utils import open_resource, get_json_resource

from twitwi.constants import TWEET_FIELDS, USER_FIELDS
from twitwi.formatters import (
    transform_tweet_into_csv_dict,
    format_tweet_as_csv_row,
    transform_user_into_csv_dict,
    format_user_as_csv_row
)


class TestFormatters(object):
    def test_transform_tweet_into_csv_dict(self):
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=TWEET_FIELDS,
            extrasaction='ignore',
            restval='',
            quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()

        with open_resource('tweet-export.jsonl') as f:
            for item in ndjson.reader(f):
                tweet = item['_source']
                transform_tweet_into_csv_dict(
                    tweet,
                    item_id=item['_id']
                )

                writer.writerow(tweet)

        with open_resource('tweet-export.csv') as f:
            output.seek(0)
            assert list(csv.DictReader(output)) == list(csv.DictReader(f))

    def test_transform_user_into_csv_dict(self):
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=USER_FIELDS,
            extrasaction='ignore',
            restval='',
            quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()

        users = get_json_resource('normalized-users.json')

        for user in users:
            transform_user_into_csv_dict(user)
            writer.writerow(user)

        with open_resource('user-export.csv') as f:
            output.seek(0)
            assert list(csv.DictReader(output)) == list(csv.DictReader(f))

    def test_format_tweet_as_csv_row(self):
        output = StringIO()

        writer = csv.writer(output)
        writer.writerow(TWEET_FIELDS)

        with open_resource('tweet-export.jsonl') as f:
            for item in ndjson.reader(f):
                tweet = item['_source']
                row = format_tweet_as_csv_row(tweet, item_id=item['_id'])

                assert len(row) == len(TWEET_FIELDS)

                writer.writerow(row)

        with open_resource('tweet-export.csv') as f:
            output.seek(0)
            assert list(csv.reader(output)) == list(csv.reader(f))

    def test_format_user_as_csv_row(self):
        output = StringIO()

        writer = csv.writer(output)
        writer.writerow(USER_FIELDS)

        users = get_json_resource('normalized-users.json')

        for user in users:
            row = format_user_as_csv_row(user)

            assert len(row) == len(USER_FIELDS)

            writer.writerow(row)

        with open_resource('user-export.csv') as f:
            output.seek(0)
            assert list(csv.reader(output)) == list(csv.reader(f))
