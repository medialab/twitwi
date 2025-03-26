import csv
from io import StringIO
from twitwi.bluesky import format_profile_as_csv_row
from twitwi.bluesky.constants import PROFILE_FIELDS
from test.utils import get_json_resource, open_resource


class TestFormatters:
    def test_format_profile_as_cs_row(self):
        normalized_profiles = get_json_resource("bluesky-normalized-profiles.json")

        buffer = StringIO(newline="")
        writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(PROFILE_FIELDS)

        for profile in normalized_profiles:
            writer.writerow(format_profile_as_csv_row(profile))

        # written = buffer.getvalue()

        # with open("test/resources/bluesky-profiles-export.csv", "w") as f:
        #     f.write(written)

        with open_resource("bluesky-profiles-export.csv") as f:
            buffer.seek(0)
            assert list(csv.reader(buffer)) == list(csv.reader(f))
