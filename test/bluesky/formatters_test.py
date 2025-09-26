import csv
from io import StringIO
from twitwi.bluesky import (
    format_profile_as_csv_row,
    format_partial_profile_as_csv_row,
    format_post_as_csv_row,
    transform_profile_into_csv_dict,
    transform_partial_profile_into_csv_dict,
    transform_post_into_csv_dict,
)
from twitwi.bluesky.constants import PROFILE_FIELDS, PARTIAL_PROFILE_FIELDS, POST_FIELDS
from test.utils import get_json_resource, open_resource


# Set to True to regenerate test results
OVERWRITE_TESTS = False


class TestFormatters:
    def test_format_profile_as_csv_row(self):
        normalized_profiles = get_json_resource("bluesky-normalized-profiles.json")

        buffer = StringIO(newline=None)
        writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(PROFILE_FIELDS)

        for profile in normalized_profiles:
            writer.writerow(format_profile_as_csv_row(profile))

        if OVERWRITE_TESTS:
            written = buffer.getvalue()

            with open("test/resources/bluesky-profiles-export.csv", "w") as f:
                f.write(written)

        with open_resource("bluesky-profiles-export.csv") as f:
            buffer.seek(0)
            assert list(csv.reader(buffer)) == list(csv.reader(f))

    def test_transform_profile_into_csv_dict(self):
        normalized_profiles = get_json_resource("bluesky-normalized-profiles.json")

        buffer = StringIO(newline=None)
        writer = csv.DictWriter(
            buffer,
            fieldnames=PROFILE_FIELDS,
            extrasaction="ignore",
            restval="",
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()

        for profile in normalized_profiles:
            transform_profile_into_csv_dict(profile)
            writer.writerow(profile)

        with open_resource("bluesky-profiles-export.csv") as f:
            buffer.seek(0)
            assert list(csv.DictReader(buffer)) == list(csv.DictReader(f))

    def test_format_partial_profile_as_csv_row(self):
        normalized_partial_profiles = get_json_resource(
            "bluesky-normalized-partial-profiles.json"
        )

        buffer = StringIO(newline=None)
        writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(PARTIAL_PROFILE_FIELDS)

        for profile in normalized_partial_profiles:
            writer.writerow(format_partial_profile_as_csv_row(profile))

        if OVERWRITE_TESTS:
            written = buffer.getvalue()

            with open("test/resources/bluesky-partial-profiles-export.csv", "w") as f:
                f.write(written)

        with open_resource("bluesky-partial-profiles-export.csv") as f:
            buffer.seek(0)
            assert list(csv.reader(buffer)) == list(csv.reader(f))

    def test_transform_partial_profile_into_csv_dict(self):
        normalized_partial_profiles = get_json_resource(
            "bluesky-normalized-partial-profiles.json"
        )

        buffer = StringIO(newline=None)
        writer = csv.DictWriter(
            buffer,
            fieldnames=PARTIAL_PROFILE_FIELDS,
            extrasaction="ignore",
            restval="",
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()

        for profile in normalized_partial_profiles:
            transform_partial_profile_into_csv_dict(profile)
            writer.writerow(profile)

        with open_resource("bluesky-partial-profiles-export.csv") as f:
            buffer.seek(0)
            assert list(csv.DictReader(buffer)) == list(csv.DictReader(f))

    def test_format_post_as_csv_row(self):
        normalized_posts = get_json_resource("bluesky-normalized-posts.json")

        buffer = StringIO(newline=None)
        writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(POST_FIELDS)

        for source in normalized_posts:
            for post in source:
                writer.writerow(format_post_as_csv_row(post))

        if OVERWRITE_TESTS:
            written = buffer.getvalue()

            with open("test/resources/bluesky-posts-export.csv", "w") as f:
                f.write(written)

        with open_resource("bluesky-posts-export.csv") as f:
            buffer.seek(0)

            assert list(csv.reader(buffer)) == list(csv.reader(f))

    def test_transform_post_into_csv_dict(self):
        normalized_posts = get_json_resource("bluesky-normalized-posts.json")

        buffer = StringIO(newline=None)
        writer = csv.DictWriter(
            buffer,
            fieldnames=POST_FIELDS,
            extrasaction="ignore",
            restval="",
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()

        for source in normalized_posts:
            for post in source:
                transform_post_into_csv_dict(post)
                writer.writerow(post)

        with open_resource("bluesky-posts-export.csv") as f:
            buffer.seek(0)
            assert list(csv.DictReader(buffer)) == list(csv.DictReader(f))
