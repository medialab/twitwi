# =============================================================================
# Twitwi Bluesky Normalizers Unit Tests
# =============================================================================
from functools import partial
from pytz import timezone

from twitwi.bluesky import normalize_profile

from test.utils import get_json_resource


def compare_dicts(_id, d1, d2, ignore_fields=[]):
    for k in d2.keys():
        if k not in ignore_fields + ["collection_time"]:
            assert d1[k] == d2[k], (
                'Different value for key "%s" with payload data for "%s"'
                % (
                    k,
                    _id,
                )
            )

    for k in d1.keys():
        if k not in ignore_fields:
            assert k in d2, 'Missing key "%s" with payload data for "%s"' % (k, _id)


class TestNormalizers:
    def test_normalize_profile(self):
        tz = timezone("Europe/Paris")

        profiles = get_json_resource("bluesky-profiles.json")
        fn = partial(normalize_profile, locale=tz)

        # from test.utils import dump_json_resource

        # normalized_profiles = [fn(profile) for profile in profiles]
        # dump_json_resource(normalized_profiles, "bluesky-normalized-profiles.json")

        expected = get_json_resource("bluesky-normalized-profiles.json")

        for idx, profile in enumerate(profiles):
            result = fn(profile)
            assert isinstance(result, dict)
            assert "collection_time" in result and isinstance(
                result["collection_time"], str
            )

            compare_dicts(profile["handle"], result, expected[idx])
