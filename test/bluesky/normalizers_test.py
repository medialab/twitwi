from twitwi.bluesky import normalize_profile

from test.utils import get_json_resource


class TestNormalizers:
    def test_normalize_profile(self):
        profiles = get_json_resource("bluesky-profiles.json")
        normalized_profiles = [normalize_profile(profile) for profile in profiles]

        # with open("test/resources/bluesky-normalized-profiles.json", "w") as f:
        #     import json

        #     json.dump(normalized_profiles, f, indent=2, ensure_ascii=False)

        expected = get_json_resource("bluesky-normalized-profiles.json")

        assert normalized_profiles == expected
