# =============================================================================
# Twitwi Bluesky Normalizers Unit Tests
# =============================================================================
from functools import partial
from pytz import timezone
from copy import deepcopy

from twitwi.bluesky import normalize_profile, normalize_partial_profile, normalize_post

from test.utils import get_json_resource


# Set to True to regenerate test results
OVERWRITE_TESTS = False


FAKE_COLLECTION_TIME = "2025-01-01T00:00:00.000000"


def set_fake_collection_time(dico):
    if "collection_time" in dico:
        dico["collection_time"] = FAKE_COLLECTION_TIME
    return dico


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

        if OVERWRITE_TESTS:
            from test.utils import dump_json_resource

            normalized_profiles = [
                set_fake_collection_time(fn(profile)) for profile in profiles
            ]
            dump_json_resource(normalized_profiles, "bluesky-normalized-profiles.json")

        expected = get_json_resource("bluesky-normalized-profiles.json")

        for idx, profile in enumerate(profiles):
            result = fn(profile)
            assert isinstance(result, dict)
            assert "collection_time" in result and isinstance(
                result["collection_time"], str
            )

            compare_dicts(profile["handle"], result, expected[idx])

    def test_normalize_profile_should_not_mutate(self):
        profile = get_json_resource("bluesky-profiles.json")[0]

        original_arg = deepcopy(profile)

        normalize_profile(profile)

        assert profile == original_arg

    def test_normalize_partial_profile(self):
        tz = timezone("Europe/Paris")

        profiles = get_json_resource("bluesky-partial-profiles.json")
        fn = partial(normalize_partial_profile, locale=tz)

        if OVERWRITE_TESTS:
            from test.utils import dump_json_resource

            normalized_profiles = [
                set_fake_collection_time(fn(profile)) for profile in profiles
            ]
            dump_json_resource(
                normalized_profiles, "bluesky-normalized-partial-profiles.json"
            )

        expected = get_json_resource("bluesky-normalized-partial-profiles.json")

        for idx, profile in enumerate(profiles):
            result = fn(profile)
            assert isinstance(result, dict)
            assert "collection_time" in result and isinstance(
                result["collection_time"], str
            )

            compare_dicts(profile["handle"], result, expected[idx])

    def test_normalize_partial_profile_should_not_mutate(self):
        profile = get_json_resource("bluesky-partial-profiles.json")[0]

        original_arg = deepcopy(profile)

        normalize_partial_profile(profile)

        assert profile == original_arg

    def test_normalize_post(self):
        tz = timezone("Europe/Paris")

        posts = get_json_resource("bluesky-posts.json")
        fn = partial(normalize_post, locale=tz)

        if OVERWRITE_TESTS:
            from test.utils import dump_json_resource

            normalized_posts = [
                [
                    set_fake_collection_time(p)
                    for p in fn(post, extract_referenced_posts=True)
                ]
                for post in posts
            ]
            dump_json_resource(normalized_posts, "bluesky-normalized-posts.json")

        expected = get_json_resource("bluesky-normalized-posts.json")

        # With referenced tweets
        for idx, post in enumerate(posts):
            result = fn(post, extract_referenced_posts=True)
            assert isinstance(result, list)
            assert set(p["uri"] for p in result) == set(p["uri"] for p in expected[idx])
            for idx2, p in enumerate(result):
                assert "collection_time" in p and isinstance(p["collection_time"], str)

                if "post" in post:
                    uri = post["post"]["uri"]
                else:
                    uri = post["uri"]
                compare_dicts(uri, p, expected[idx][idx2])

        # With single output
        for idx, post in enumerate(posts):
            result = fn(post)

            assert isinstance(result, dict)

            _id = p["uri"]
            compare_dicts(_id, result, expected[idx][-1])

        # With custom collection_source
        for post in posts:
            result = fn(post, collection_source="unit_test")

            assert result["collected_via"] == ["unit_test"]

    def test_normalize_post_should_not_mutate(self):
        post = get_json_resource("bluesky-posts.json")[0]

        original_arg = deepcopy(post)

        normalize_post(post)

        assert post == original_arg

    def test_normalize_post_should_be_normalized_across_sources(self):
        # handle same post from different sources (search, get_post and user_feed)
        pass

    def test_badly_formatted_posts_payload(self):
        pass
