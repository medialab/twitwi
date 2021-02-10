# =============================================================================
# Twitwi Formatters Unit Tests
# =============================================================================
import ndjson
import csv
from io import StringIO
from test.utils import open_resource

from twitwi.constants import TWEET_FIELDS
from twitwi.formatters import transform_tweet_into_csv_dict


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
                    tweet_id=item['_id']
                )

                writer.writerow(tweet)

        with open_resource('tweet-export.csv') as f:
            output.seek(0)
            assert list(csv.DictReader(output)) == list(csv.DictReader(f))
