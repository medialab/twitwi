# =============================================================================
# Twitwi Anonymizers Unit Tests
# =============================================================================
import csv
from io import StringIO

from test.utils import get_json_resource

from twitwi.constants import TWEET_FIELDS
from twitwi.anonymizers import anonymize_normalized_tweet, redact_quoted_text, redact_rt_text
from twitwi.formatters import transform_tweet_into_csv_dict


class TestAnonymizers(object):
    def test_redact_quoted_text(self):
        assert redact_quoted_text("test « bidule: voilà voilà »") == "test « voilà voilà »"

    def test_redact_rt_text(self):
        assert redact_rt_text("RT @bidule: voilà voilà") == "RT: voilà voilà"

    def test_anonymize_normalized_tweet(self):
        tweets = get_json_resource("normalized-tweets-v2-all.json")
        tweets_index = {t["id"]: t for t in tweets}

        normal_tweet = tweets_index["1382840699322732544"]
        reply_tweet = tweets_index["1383054846186639361"]
        quote_tweet = tweets_index["1383018622486863883"]
        retweet = tweets_index["1383054697423015942"]

        anonymize_normalized_tweet(normal_tweet)
        anonymize_normalized_tweet(reply_tweet)
        anonymize_normalized_tweet(quote_tweet)
        anonymize_normalized_tweet(retweet)

        transform_tweet_into_csv_dict(normal_tweet)
        transform_tweet_into_csv_dict(reply_tweet)
        transform_tweet_into_csv_dict(quote_tweet)
        transform_tweet_into_csv_dict(retweet)

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=TWEET_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerow(normal_tweet)
        writer.writerow(reply_tweet)
        writer.writerow(quote_tweet)
        writer.writerow(retweet)

        rows = list(csv.reader(StringIO(output.getvalue())))

        assert rows == [
            ['id', 'timestamp_utc', 'local_time', 'user_screen_name', 'text', 'possibly_sensitive', 'retweet_count', 'like_count', 'reply_count', 'impression_count', 'lang', 'to_username', 'to_userid', 'to_tweetid', 'source_name', 'source_url', 'user_location', 'lat', 'lng', 'user_id', 'user_name', 'user_verified', 'user_description', 'user_url', 'user_image', 'user_tweets', 'user_followers', 'user_friends', 'user_likes', 'user_lists', 'user_created_at', 'user_timestamp_utc', 'collected_via', 'match_query', 'retweeted_id', 'retweeted_user', 'retweeted_user_id', 'retweeted_timestamp_utc', 'quoted_id', 'quoted_user', 'quoted_user_id', 'quoted_timestamp_utc', 'collection_time', 'url', 'place_country_code', 'place_name', 'place_type', 'place_coordinates', 'links', 'domains', 'media_urls', 'media_files', 'media_types', 'media_alt_texts', 'mentioned_names', 'mentioned_ids', 'hashtags'],
            ['1382840699322732544', '1618529889', '2021-04-15T23:38:09', '', 'Repost from @joselcherrez\n•\n#tbt \n7 years ago! \n#executiveprotection #usa #joselcherrez #bodyguardsforlife #tbthursday #teamgeprotection #trump #tbt🔙📸 \nNo caption needed. #nocaptionneeded \n#merica🇺🇸 @ Miami, Florida https://www.instagram.com/p/CNtJAKLFccf/?igshid=1f77wfinfvpre', '0', '1', '1', '0', '', 'en', '', '', '', 'Instagram', '', '', '', '', '', '', '', '', '', '', '2787', '1663', '286', '', '15', '', '', 'retweet|test', '1', '', '', '', '', '', '', '', '', '2022-07-29T12:34:28.984748', '', '', '', '', '', 'https://www.instagram.com/p/CNtJAKLFccf/', '', '', '', '', '', 'joselcherrez', '1094092760', 'bodyguardsforlife|executiveprotection|joselcherrez|merica|nocaptionneeded|tbt|tbthursday|teamgeprotection|trump|usa'],
            ['1383054846186639361', '1618580945', '2021-04-16T13:49:05', '', '@johanwadenback @Andromake000 @Expressen Det är bara att läsa vad som själva CDC säger och sluta vilseleda jävla #covidiot https://twitter.com/toknell/status/1383054846186639361/photo/1', '0', '0', '0', '0', '', 'sv', '', '', '1383054056906711040', 'Twitter for iPhone', '', '', '', '', '', '', '', '', '', '', '20948', '462', '213', '', '8', '', '', 'test', '1', '', '', '', '', '', '', '', '', '2022-07-29T12:34:28.984483', '', '', '', '', '', 'https://twitter.com/toknell/status/1383054846186639361/photo/1', '', 'https://pbs.twimg.com/media/EzGZDN4XAAAwSQS.jpg', '1383054846186639361_EzGZDN4XAAAwSQS.jpg', 'photo', '', 'Andromake000|Expressen|johanwadenback', '2893142548|2097191|1000827618546110464', 'covidiot'],
            ['1383018622486863883', '1618572309', '2021-04-16T11:25:09', '', 'The only thing that can come out of taking this #AYUSH pledge is more #liver #transplantation in #India due to #giloy and #Ashwagandha.\n#Ayurveda #pseudoscience #quackery\n\nPledge 2\n➡️wear #Masks\n➡️avoid festivities, ceremonies.\n➡️#vaccinate #vaccination\n➡️not be a #COVIDIOT https://twitter.com/mygovindia/status/1382607043240988673', '0', '9', '15', '1', '', 'en', '', '', '', 'Twitter for Android', '', '', '', '', '', '', '', '', '', '', '6082', '4554', '372', '', '42', '', '', 'retweet', '1', '', '', '', '', '1382607043240988673', '', '', '', '2022-07-29T12:34:28.984417', '', '', '', '', '', 'https://twitter.com/mygovindia/status/1382607043240988673', '', '', '', '', '', '', '', 'AYUSH|Ashwagandha|Ayurveda|COVIDIOT|India|Masks|giloy|liver|pseudoscience|quackery|transplantation|vaccinate|vaccination'],
            ['1383054697423015942', '1618580910', '2021-04-16T13:48:30', '', 'RT: Central minister Mr V Muraleedharan is reported to have described CM, Kerala as a "Covidiot". Shocking \n\nIs there no one in the BJP\'s leadership who will reprimand the minister for using unacceptable language?', '0', '0', '0', '0', '', 'en', '', '', '', 'Twitter for Android', '', '', '', '', '', '', '', '', '', '', '5098', '133', '1931', '', '0', '', '', 'test', '1', '1383026700695441414', '', '', '', '', '', '', '', '2022-07-29T12:34:28.984642', '', '', '', '', '', '', '', '', '', '', '', 'PChidambaram_IN', '3097503906', '']
        ]
