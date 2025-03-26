from twitwi.bluesky import normalize_profile

from test.utils import get_json_resource


class TestNormalizers:
    def test_normalize_profile(self):
        profiles = get_json_resource("bluesky-profiles.json")
        normalized_profiles = [normalize_profile(profile) for profile in profiles]

        # from test.utils import dump_json_resource

        # dump_json_resource(normalized_profiles, "bluesky-normalized-profiles.json")

        expected = get_json_resource("bluesky-normalized-profiles.json")

        assert normalized_profiles == expected
