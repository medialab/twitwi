# =============================================================================
# Twitwi Utilities Unit Tests
# =============================================================================
from pytz import timezone
from twitwi.utils import get_dates, prepare_tweet

GET_DATES_TESTS = [
    (('Thu Feb 07 06:43:33 +0000 2013', 'Europe/Paris'), (1360219413, '2013-02-07T07:43:33')),
    (('Tue Nov 24 16:43:53 +0000 2020', 'Europe/Paris'), (1606236233, '2020-11-24T17:43:53')),
    (('Tue Nov 24 16:52:48 +0000 2020', 'Australia/Adelaide'), (1606236768, '2020-11-25T03:22:48'))
]

PREPARE_TWEET_TEST = [
    (
        {'created_at': 'Fri Jan 29 16:29:05 +0000 2021', 'id_str': '1355191242137743365', 'text': 'RT @NickKnudsenUS: Everyone: Biden won.\nGOP: He cheated!\nEveryone: Evidence?\nGOP: We said so.\nEveryone: That\'s not evidence.\nGOP: You\'re tr\u2026', 'source': '<a href="http://twitter.com/download/android" rel="nofollow">Twitter for Android</a>', 'truncated': False, 'in_reply_to_status_id': None, 'in_reply_to_status_id_str': None, 'in_reply_to_user_id': None, 'in_reply_to_user_id_str': None, 'in_reply_to_screen_name': None, 'user': {'id': 1350513055, 'id_str': '1350513055', 'name': 'MsDreadNoMore\ud83c\udf0a\ud83c\uddfa\ud83c\uddf8 #Biden2020', 'screen_name': 'debmapmom2', 'location': 'Edmond, OK', 'url': None, 'description': 'WEAR A FREAKING MASK! I am antifa!  \nI\'d rather be hated for being myself than loved for who I\'m not...Kurt Cobain \n#fbr #resist #BLM', 'translator_type': 'none', 'protected': False, 'verified': False, 'followers_count': 4121, 'friends_count': 4977, 'listed_count': 5, 'favourites_count': 72502, 'statuses_count': 4418, 'created_at': 'Sat Apr 13 23:39:20 +0000 2013', 'utc_offset': None, 'time_zone': None, 'geo_enabled': True, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'profile_background_color': 'C0DEED', 'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_tile': False, 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'profile_image_url': 'http://pbs.twimg.com/profile_images/1352483266943721475/Z4qPzA9T_normal.jpg', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1352483266943721475/Z4qPzA9T_normal.jpg', 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/1350513055/1611292161', 'default_profile': True, 'default_profile_image': False, 'following': None, 'follow_request_sent': None, 'notifications': None}, 'geo': None, 'coordinates': None, 'place': None, 'contributors': None, 'retweeted_status': {'created_at': 'Fri Jan 29 06:54:36 +0000 2021', 'id': 1355046668995977219, 'id_str': '1355046668995977219', 'text': 'Everyone: Biden won.\nGOP: He cheated!\nEveryone: Evidence?\nGOP: We said so.\nEveryone: That\'s not evidence.\nGOP: You\'\u2026 https://t.co/WDj7ABMVAb', 'source': '<a href="https://mobile.twitter.com" rel="nofollow">Twitter Web App</a>', 'truncated': True, 'in_reply_to_status_id': None, 'in_reply_to_status_id_str': None, 'in_reply_to_user_id': None, 'in_reply_to_user_id_str': None, 'in_reply_to_screen_name': None, 'user': {'id': 798953701972938752, 'id_str': '798953701972938752', 'name': 'Nick Knudsen \ud83c\uddfa\ud83c\uddf8', 'screen_name': 'NickKnudsenUS', 'location': 'Portland, OR', 'url': 'http://www.demcastusa.com', 'description': 'Executive Director @DemCastUSA \ud83c\uddfa\ud83c\uddf8 Formerly: Editor-In-Chief, DemWritePress. Writing: @HuffPost @PatNotPart. We still have a lot of work to do. #DemCast', 'translator_type': 'none', 'protected': False, 'verified': False, 'followers_count': 195281, 'friends_count': 15570, 'listed_count': 796, 'favourites_count': 75320, 'statuses_count': 65634, 'created_at': 'Wed Nov 16 18:19:41 +0000 2016', 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'profile_background_color': '000000', 'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_tile': False, 'profile_link_color': '19CF86', 'profile_sidebar_border_color': '000000', 'profile_sidebar_fill_color': '000000', 'profile_text_color': '000000', 'profile_use_background_image': False, 'profile_image_url': 'http://pbs.twimg.com/profile_images/1252470219232014337/5mzgTlRw_normal.jpg', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1252470219232014337/5mzgTlRw_normal.jpg', 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/798953701972938752/1611643068', 'default_profile': False, 'default_profile_image': False, 'following': None, 'follow_request_sent': None, 'notifications': None}, 'geo': None, 'coordinates': None, 'place': None, 'contributors': None, 'is_quote_status': False, 'extended_tweet': {'full_text': 'Everyone: Biden won.\nGOP: He cheated!\nEveryone: Evidence?\nGOP: We said so.\nEveryone: That\'s not evidence.\nGOP: You\'re trying to steal the election!\nEveryone: That\'s *literally* what you\'re doing.\nGOP: We must revolt!\nCrazies: Revolt!\nEveryone: You\'re traitors.\nGOP: Don\'t be mean.', 'display_text_range': [0, 280], 'entities': {'hashtags': [], 'urls': [], 'user_mentions': [], 'symbols': []}}, 'quote_count': 397, 'reply_count': 317, 'retweet_count': 8297, 'favorite_count': 33427, 'entities': {'hashtags': [], 'urls': [{'url': 'https://t.co/WDj7ABMVAb', 'expanded_url': 'https://twitter.com/i/web/status/1355046668995977219', 'display_url': 'twitter.com/i/web/status/1\u2026', 'indices': [117, 140]}], 'user_mentions': [], 'symbols': []}, 'favorited': False, 'retweeted': False, 'filter_level': 'low', 'lang': 'en'}, 'is_quote_status': False, 'quote_count': 0, 'reply_count': 0, 'retweet_count': 0, 'favorite_count': 0, 'entities': {'hashtags': [], 'urls': [], 'user_mentions': [{'screen_name': 'NickKnudsenUS', 'name': 'Nick Knudsen \ud83c\uddfa\ud83c\uddf8', 'id': 798953701972938752, 'id_str': '798953701972938752', 'indices': [3, 17]}], 'symbols': []}, 'favorited': False, 'retweeted': False, 'filter_level': 'low', 'lang': 'en', 'timestamp_ms': '1611937745018', 'gazouilloire_source': 'stream'},
        [{'_id': '1355046668995977219', 'local_time': '2021-01-29T07:54:36', 'timestamp_utc': 1611903276.0, 'text': 'Everyone: Biden won.\nGOP: He cheated!\nEveryone: Evidence?\nGOP: We said so.\nEveryone: That\'s not evidence.\nGOP: You\'re trying to steal the election!\nEveryone: That\'s *literally* what you\'re doing.\nGOP: We must revolt!\nCrazies: Revolt!\nEveryone: You\'re traitors.\nGOP: Don\'t be mean.', 'url': 'https://twitter.com/NickKnudsenUS/statuses/1355046668995977219', 'quoted_id': None, 'quoted_user': None, 'quoted_user_id': None, 'quoted_timestamp_utc': None, 'retweeted_id': None, 'retweeted_user': None, 'retweeted_user_id': None, 'retweeted_timestamp_utc': None, 'media_files': [], 'media_types': [], 'media_urls': [], 'links': [], 'links_to_resolve': False, 'hashtags': [], 'mentioned_ids': [], 'mentioned_names': [], 'collection_time': '2021-01-29T17:29:10.218648', 'collected_via': ['retweet'], 'match_query': True, 'to_tweetid': None, 'to_username': None, 'to_userid': None, 'lang': 'en', 'coordinates': None, 'retweet_count': 8297, 'like_count': 33427, 'reply_count': 317, 'user_id': '798953701972938752', 'user_screen_name': 'NickKnudsenUS', 'user_name': 'Nick Knudsen \ud83c\uddfa\ud83c\uddf8', 'user_friends': 15570, 'user_followers': 195281, 'user_location': 'Portland, OR', 'user_verified': False, 'user_description': 'Executive Director @DemCastUSA \ud83c\uddfa\ud83c\uddf8 Formerly: Editor-In-Chief, DemWritePress. Writing: @HuffPost @PatNotPart. We still have a lot of work to do. #DemCast', 'user_created_at': '2016-11-16T19:19:41', 'user_tweets': 65634, 'user_likes': 75320, 'user_lists': 796, 'user_image': 'https://pbs.twimg.com/profile_images/1252470219232014337/5mzgTlRw_normal.jpg', 'user_url': 'http://www.demcastusa.com', 'user_timestamp_utc': 1479320381.0, 'source_url': 'https://mobile.twitter.com', 'source_name': 'Twitter Web App'}]
    ),
    (
        {'created_at': 'Fri Jan 29 06:54:36 +0000 2021', 'id_str': '1355046668995977219', 'text': 'Everyone: Biden won.\nGOP: He cheated!\nEveryone: Evidence?\nGOP: We said so.\nEveryone: That\'s not evidence.\nGOP: You\'\u2026 https://t.co/WDj7ABMVAb', 'source': '<a href="https://mobile.twitter.com" rel="nofollow">Twitter Web App</a>', 'truncated': True, 'in_reply_to_status_id': None, 'in_reply_to_status_id_str': None, 'in_reply_to_user_id': None, 'in_reply_to_user_id_str': None, 'in_reply_to_screen_name': None, 'user': {'id': 798953701972938752, 'id_str': '798953701972938752', 'name': 'Nick Knudsen \ud83c\uddfa\ud83c\uddf8', 'screen_name': 'NickKnudsenUS', 'location': 'Portland, OR', 'url': 'http://www.demcastusa.com', 'description': 'Executive Director @DemCastUSA \ud83c\uddfa\ud83c\uddf8 Formerly: Editor-In-Chief, DemWritePress. Writing: @HuffPost @PatNotPart. We still have a lot of work to do. #DemCast', 'translator_type': 'none', 'protected': False, 'verified': False, 'followers_count': 195281, 'friends_count': 15570, 'listed_count': 796, 'favourites_count': 75320, 'statuses_count': 65634, 'created_at': 'Wed Nov 16 18:19:41 +0000 2016', 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'profile_background_color': '000000', 'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_tile': False, 'profile_link_color': '19CF86', 'profile_sidebar_border_color': '000000', 'profile_sidebar_fill_color': '000000', 'profile_text_color': '000000', 'profile_use_background_image': False, 'profile_image_url': 'http://pbs.twimg.com/profile_images/1252470219232014337/5mzgTlRw_normal.jpg', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1252470219232014337/5mzgTlRw_normal.jpg', 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/798953701972938752/1611643068', 'default_profile': False, 'default_profile_image': False, 'following': None, 'follow_request_sent': None, 'notifications': None}, 'geo': None, 'coordinates': None, 'place': None, 'contributors': None, 'is_quote_status': False, 'extended_tweet': {'full_text': 'Everyone: Biden won.\nGOP: He cheated!\nEveryone: Evidence?\nGOP: We said so.\nEveryone: That\'s not evidence.\nGOP: You\'re trying to steal the election!\nEveryone: That\'s *literally* what you\'re doing.\nGOP: We must revolt!\nCrazies: Revolt!\nEveryone: You\'re traitors.\nGOP: Don\'t be mean.', 'display_text_range': [0, 280], 'entities': {'hashtags': [], 'urls': [], 'user_mentions': [], 'symbols': []}}, 'quote_count': 397, 'reply_count': 317, 'retweet_count': 8297, 'favorite_count': 33427, 'entities': {'hashtags': [], 'urls': [{'url': 'https://t.co/WDj7ABMVAb', 'expanded_url': 'https://twitter.com/i/web/status/1355046668995977219', 'display_url': 'twitter.com/i/web/status/1\u2026', 'indices': [117, 140]}], 'user_mentions': [], 'symbols': []}, 'favorited': False, 'retweeted': False, 'filter_level': 'low', 'lang': 'en', 'gazouilloire_source': 'retweet'},
        [{'_id': '1355046668995977219', 'local_time': '2021-01-29T07:54:36', 'timestamp_utc': 1611903276.0, 'text': 'Everyone: Biden won.\nGOP: He cheated!\nEveryone: Evidence?\nGOP: We said so.\nEveryone: That\'s not evidence.\nGOP: You\'re trying to steal the election!\nEveryone: That\'s *literally* what you\'re doing.\nGOP: We must revolt!\nCrazies: Revolt!\nEveryone: You\'re traitors.\nGOP: Don\'t be mean.', 'url': 'https://twitter.com/NickKnudsenUS/statuses/1355046668995977219', 'quoted_id': None, 'quoted_user': None, 'quoted_user_id': None, 'quoted_timestamp_utc': None, 'retweeted_id': None, 'retweeted_user': None, 'retweeted_user_id': None, 'retweeted_timestamp_utc': None, 'media_files': [], 'media_types': [], 'media_urls': [], 'links': [], 'links_to_resolve': False, 'hashtags': [], 'mentioned_ids': [], 'mentioned_names': [], 'collection_time': '2021-01-29T17:29:10.218648', 'collected_via': ['retweet'], 'match_query': True, 'to_tweetid': None, 'to_username': None, 'to_userid': None, 'lang': 'en', 'coordinates': None, 'retweet_count': 8297, 'like_count': 33427, 'reply_count': 317, 'user_id': '798953701972938752', 'user_screen_name': 'NickKnudsenUS', 'user_name': 'Nick Knudsen \ud83c\uddfa\ud83c\uddf8', 'user_friends': 15570, 'user_followers': 195281, 'user_location': 'Portland, OR', 'user_verified': False, 'user_description': 'Executive Director @DemCastUSA \ud83c\uddfa\ud83c\uddf8 Formerly: Editor-In-Chief, DemWritePress. Writing: @HuffPost @PatNotPart. We still have a lot of work to do. #DemCast', 'user_created_at': '2016-11-16T19:19:41', 'user_tweets': 65634, 'user_likes': 75320, 'user_lists': 796, 'user_image': 'https://pbs.twimg.com/profile_images/1252470219232014337/5mzgTlRw_normal.jpg', 'user_url': 'http://www.demcastusa.com', 'user_timestamp_utc': 1479320381.0, 'source_url': 'https://mobile.twitter.com', 'source_name': 'Twitter Web App'}, {'_id': '1355191242137743365', 'local_time': '2021-01-29T17:29:05', 'timestamp_utc': 1611937745.0, 'text': 'RT @NickKnudsenUS: Everyone: Biden won.\nGOP: He cheated!\nEveryone: Evidence?\nGOP: We said so.\nEveryone: That\'s not evidence.\nGOP: You\'re trying to steal the election!\nEveryone: That\'s *literally* what you\'re doing.\nGOP: We must revolt!\nCrazies: Revolt!\nEveryone: You\'re traitors.\nGOP: Don\'t be mean.', 'url': 'https://twitter.com/debmapmom2/statuses/1355191242137743365', 'quoted_id': None, 'quoted_user': None, 'quoted_user_id': None, 'quoted_timestamp_utc': None, 'retweeted_id': '1355046668995977219', 'retweeted_user': 'NickKnudsenUS', 'retweeted_user_id': '798953701972938752', 'retweeted_timestamp_utc': 1611903276.0, 'media_files': [], 'media_types': [], 'media_urls': [], 'links': [], 'links_to_resolve': False, 'hashtags': [], 'mentioned_ids': ['798953701972938752'], 'mentioned_names': ['nickknudsenus'], 'collection_time': '2021-01-29T17:29:10.220398', 'collected_via': ['stream'], 'match_query': True, 'to_tweetid': None, 'to_username': None, 'to_userid': None, 'lang': 'en', 'coordinates': None, 'retweet_count': 0, 'like_count': 0, 'reply_count': 0, 'user_id': '1350513055', 'user_screen_name': 'debmapmom2', 'user_name': 'MsDreadNoMore\ud83c\udf0a\ud83c\uddfa\ud83c\uddf8 #Biden2020', 'user_friends': 4977, 'user_followers': 4121, 'user_location': 'Edmond, OK', 'user_verified': False, 'user_description': 'WEAR A FREAKING MASK! I am antifa!  \nI\'d rather be hated for being myself than loved for who I\'m not...Kurt Cobain \n#fbr #resist #BLM', 'user_created_at': '2013-04-14T01:39:20', 'user_tweets': 4418, 'user_likes': 72502, 'user_lists': 5, 'user_image': 'https://pbs.twimg.com/profile_images/1352483266943721475/Z4qPzA9T_normal.jpg', 'user_url': None, 'user_timestamp_utc': 1365896360.0, 'source_url': 'http://twitter.com/download/android', 'source_name': 'Twitter for Android'}]

    ),
    (
        {'created_at': 'Mon Feb 01 17:10:06 +0000 2021', 'id': 1356288731519479810, 'id_str': '1356288731519479810', 'full_text': '\u23f0\u25062/1  26\u6642\u534a start\u2764\ud83d\udc97\n\ud83d\udc64\u2506\u30c7\u30e5\u30aa\n\ud83d\udcb8\u2506500 \u00d72  \u307a\u3044\u307a\u3044\n\n\u30d1\u30b9\u30c4\u30a4Just\n \u25b6 @neosuke1203\n\n\u30ea\u30b6\u30eb\u30c8\u63d0\u51fa\u5148\n\u25b6 @kananba_1\n#\u30c7\u30e5\u30aa #26\u6642\u534a\n#\u30c7\u30e5\u30aa\u30b2\u30ea\u30e9 \n#\u30c7\u30e5\u30aa26\u6642\u534a https://t.co/hjLyHeg0Bl', 'truncated': False, 'display_text_range': [0, 117], 'entities': {'hashtags': [{'text': '\u30c7\u30e5\u30aa', 'indices': [89, 93]}, {'text': '26\u6642\u534a', 'indices': [94, 99]}, {'text': '\u30c7\u30e5\u30aa\u30b2\u30ea\u30e9', 'indices': [100, 107]}, {'text': '\u30c7\u30e5\u30aa26\u6642\u534a', 'indices': [109, 117]}], 'symbols': [], 'user_mentions': [{'screen_name': 'neosuke1203', 'name': '\u306d\u304a\u3059\u3051', 'id': 1068760421371326464, 'id_str': '1068760421371326464', 'indices': [54, 66]}, {'screen_name': 'kananba_1', 'name': 'kana*\ud83d\udc3b\u2764', 'id': 1115927821925277701, 'id_str': '1115927821925277701', 'indices': [78, 88]}], 'urls': [{'url': 'https://t.co/hjLyHeg0Bl', 'expanded_url': 'https://twitter.com/rizu_1122/status/1356256391653019649', 'display_url': 'twitter.com/rizu_1122/stat\u2026', 'indices': [118, 141]}]}, 'metadata': {'iso_language_code': 'ja', 'result_type': 'recent'}, 'source': '<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>', 'in_reply_to_status_id': None, 'in_reply_to_status_id_str': None, 'in_reply_to_user_id': None, 'in_reply_to_user_id_str': None, 'in_reply_to_screen_name': None, 'user': {'id': 1165568564843048960, 'id_str': '1165568564843048960', 'name': '\u3074\u308d\u3010\u305e\u308f\u72c2\u3011', 'screen_name': 'piiro08', 'location': '\u65e5\u672c', 'description': '\u8352\u91ce\u57a2\u3067\u3059\ud83d\ude0a\u4e3b\u50ac\u3082\u3057\u3066\u308b\u3057\u30b2\u30ea\u30e9\u3082\u51fa\u3066\u308b\u306e\u304a\u9858\u3044\u3057\u307e\u3059\uff01 @zowa008\u4fe1\u8005\ud83d\ude0d', 'url': None, 'entities': {'description': {'urls': []}}, 'protected': False, 'followers_count': 282, 'friends_count': 713, 'listed_count': 0, 'created_at': 'Sun Aug 25 10:16:27 +0000 2019', 'favourites_count': 423, 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'verified': False, 'statuses_count': 519, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': 'F5F8FA', 'profile_background_image_url': None, 'profile_background_image_url_https': None, 'profile_background_tile': False, 'profile_image_url': 'http://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png', 'profile_image_url_https': 'https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png', 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'has_extended_profile': False, 'default_profile': True, 'default_profile_image': True, 'following': False, 'follow_request_sent': False, 'notifications': False, 'translator_type': 'none'}, 'geo': None, 'coordinates': None, 'place': None, 'contributors': None, 'is_quote_status': True, 'quoted_status_id': 1356256391653019649, 'quoted_status_id_str': '1356256391653019649', 'quoted_status': {'created_at': 'Mon Feb 01 15:01:36 +0000 2021', 'id': 1356256391653019649, 'id_str': '1356256391653019649', 'full_text': '\u304b\u306a\u308a\u305a\u308b\u30fc\u3080\u273f"\n\u9023\u6226"2"\n\ud83d\udcc5\u3000#2\u67081\u65e5\n\n\u23f0\u300026:30\n\n\ud83e\udd47\u3000500\u00d72 (pay)\n\n\ud83d\udc3b\u3000#\u30c7\u30e5\u30aa\n\n\u3010\u6761\u4ef6\u3011 @kananba_1/ @rizu_1122\n                follow&amp;RT \n\n\u3010\u30ea\u30d7\u3011\u4ee3\u8868\u8005ID\u306e\u307f\u62e1\u6563\u512a\u5148\n\n\u3010\u30d1\u30b9\u30c4\u30a4\u3011just\u2192  @neosuke1203\n\u4ea4\u63db\u67a0\u306a\u3069\u8ffd\u8a18\u2b07\n#\u30c7\u30e5\u30aa\u30b2\u30ea\u30e9\n#\u30c7\u30e5\u30aa26\u6642\u534a https://t.co/ZCkU5t831m', 'truncated': False, 'display_text_range': [0, 185], 'entities': {'hashtags': [{'text': '2\u67081\u65e5', 'indices': [18, 23]}, {'text': '\u30c7\u30e5\u30aa', 'indices': [51, 55]}, {'text': '\u30c7\u30e5\u30aa\u30b2\u30ea\u30e9', 'indices': [169, 176]}, {'text': '\u30c7\u30e5\u30aa26\u6642\u534a', 'indices': [177, 185]}], 'symbols': [], 'user_mentions': [{'screen_name': 'kananba_1', 'name': 'kana*\ud83d\udc3b\u2764', 'id': 1115927821925277701, 'id_str': '1115927821925277701', 'indices': [62, 72]}, {'screen_name': 'rizu_1122', 'name': '\u3084\u3093\u3067\u308c\u3006\u308a\u305a\u3042\ud83d\udd2a\u4eca\u65e5\u25b6\u30b3\u30e9\u30dc', 'id': 1143349673995853824, 'id_str': '1143349673995853824', 'indices': [74, 84]}, {'screen_name': 'neosuke1203', 'name': '\u306d\u304a\u3059\u3051', 'id': 1068760421371326464, 'id_str': '1068760421371326464', 'indices': [147, 159]}], 'urls': [], 'media': [{'id': 1356256376440246272, 'id_str': '1356256376440246272', 'indices': [186, 209], 'media_url': 'http://pbs.twimg.com/media/EtJj_RYUUAAAph9.jpg', 'media_url_https': 'https://pbs.twimg.com/media/EtJj_RYUUAAAph9.jpg', 'url': 'https://t.co/ZCkU5t831m', 'display_url': 'pic.twitter.com/ZCkU5t831m', 'expanded_url': 'https://twitter.com/rizu_1122/status/1356256391653019649/photo/1', 'type': 'photo', 'sizes': {'thumb': {'w': 150, 'h': 150, 'resize': 'crop'}, 'small': {'w': 680, 'h': 383, 'resize': 'fit'}, 'large': {'w': 2048, 'h': 1152, 'resize': 'fit'}, 'medium': {'w': 1200, 'h': 675, 'resize': 'fit'}}}]}, 'extended_entities': {'media': [{'id': 1356256376440246272, 'id_str': '1356256376440246272', 'indices': [186, 209], 'media_url': 'http://pbs.twimg.com/media/EtJj_RYUUAAAph9.jpg', 'media_url_https': 'https://pbs.twimg.com/media/EtJj_RYUUAAAph9.jpg', 'url': 'https://t.co/ZCkU5t831m', 'display_url': 'pic.twitter.com/ZCkU5t831m', 'expanded_url': 'https://twitter.com/rizu_1122/status/1356256391653019649/photo/1', 'type': 'photo', 'sizes': {'thumb': {'w': 150, 'h': 150, 'resize': 'crop'}, 'small': {'w': 680, 'h': 383, 'resize': 'fit'}, 'large': {'w': 2048, 'h': 1152, 'resize': 'fit'}, 'medium': {'w': 1200, 'h': 675, 'resize': 'fit'}}}]}, 'metadata': {'iso_language_code': 'ja', 'result_type': 'recent'}, 'source': '<a href="http://twitter.com/download/android" rel="nofollow">Twitter for Android</a>', 'in_reply_to_status_id': None, 'in_reply_to_status_id_str': None, 'in_reply_to_user_id': None, 'in_reply_to_user_id_str': None, 'in_reply_to_screen_name': None, 'user': {'id': 1143349673995853824, 'id_str': '1143349673995853824', 'name': '\ud83c\udfe1739\u3006\u308a\u305a\u3042\ud83d\udd2a\u4eca\u65e5\u25b6\u30b3\u30e9\u30dc\u9023\u6226', 'screen_name': 'rizu_1122', 'location': '', 'description': '\u50d5\u306e\u3070\u304b\ud83d\udc8d\u25b6@Ste11a_29 \ud83d\udc8d\u25b6@Ixx__17 \u5ac1\u304c\u623b\u308b\u307e\u3067\u754c\u9688\u53bb\u3089\u306a\u3044\u3088\u3002\u65e9\u304f\u623b\u3063\u3066\u304d\u3066\u25b6@Rey3222\u2665\u25b6@Sagiri_u3u                         \u30de\u30cd\u5148\u25b6@ruitya3 \n\ud83d\udc99\u25b6#\u308a\u305a\u3057\u3070\u5b9f\u7e3e', 'url': None, 'entities': {'description': {'urls': []}}, 'protected': False, 'followers_count': 3572, 'friends_count': 351, 'listed_count': 4, 'created_at': 'Tue Jun 25 02:46:19 +0000 2019', 'favourites_count': 8087, 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'verified': False, 'statuses_count': 9204, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': 'F5F8FA', 'profile_background_image_url': None, 'profile_background_image_url_https': None, 'profile_background_tile': False, 'profile_image_url': 'http://pbs.twimg.com/profile_images/1356185388486852612/ksMmkZbF_normal.jpg', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1356185388486852612/ksMmkZbF_normal.jpg', 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/1143349673995853824/1611729353', 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'has_extended_profile': False, 'default_profile': True, 'default_profile_image': False, 'following': False, 'follow_request_sent': False, 'notifications': False, 'translator_type': 'none'}, 'geo': None, 'coordinates': None, 'place': None, 'contributors': None, 'is_quote_status': False, 'retweet_count': 44, 'favorite_count': 33, 'favorited': False, 'retweeted': False, 'possibly_sensitive': False, 'lang': 'ja'}, 'retweet_count': 0, 'favorite_count': 0, 'favorited': False, 'retweeted': False, 'possibly_sensitive': True, 'lang': 'ja', 'gazouilloire_source': 'search'},
        [{'_id': '1356256391653019649', 'local_time': '2021-02-01T16:01:36', 'timestamp_utc': 1612191696.0, 'text': '\u304b\u306a\u308a\u305a\u308b\u30fc\u3080\u273f"\n\u9023\u6226"2"\n\ud83d\udcc5\u3000#2\u67081\u65e5\n\n\u23f0\u300026:30\n\n\ud83e\udd47\u3000500\u00d72 (pay)\n\n\ud83d\udc3b\u3000#\u30c7\u30e5\u30aa\n\n\u3010\u6761\u4ef6\u3011 @kananba_1/ @rizu_1122\n                follow&RT \n\n\u3010\u30ea\u30d7\u3011\u4ee3\u8868\u8005ID\u306e\u307f\u62e1\u6563\u512a\u5148\n\n\u3010\u30d1\u30b9\u30c4\u30a4\u3011just\u2192  @neosuke1203\n\u4ea4\u63db\u67a0\u306a\u3069\u8ffd\u8a18\u2b07\n#\u30c7\u30e5\u30aa\u30b2\u30ea\u30e9\n#\u30c7\u30e5\u30aa26\u6642\u534a https://twitter.com/rizu_1122/status/1356256391653019649/photo/1', 'url': 'https://twitter.com/rizu_1122/statuses/1356256391653019649', 'quoted_id': None, 'quoted_user': None, 'quoted_user_id': None, 'quoted_timestamp_utc': None, 'retweeted_id': None, 'retweeted_user': None, 'retweeted_user_id': None, 'retweeted_timestamp_utc': None, 'media_files': ['1356256391653019649_EtJj_RYUUAAAph9.jpg'], 'media_types': ['photo'], 'media_urls': ['https://pbs.twimg.com/media/EtJj_RYUUAAAph9.jpg'], 'links': [], 'links_to_resolve': False, 'hashtags': ['2\u67081\u65e5', '\u30c7\u30e5\u30aa', '\u30c7\u30e5\u30aa26\u6642\u534a', '\u30c7\u30e5\u30aa\u30b2\u30ea\u30e9'], 'mentioned_ids': ['1115927821925277701', '1068760421371326464', '1143349673995853824'], 'mentioned_names': ['kananba_1', 'neosuke1203', 'rizu_1122'], 'collection_time': '2021-02-01T18:12:22.376610', 'collected_via': ['quote'], 'match_query': False, 'to_tweetid': None, 'to_username': None, 'to_userid': None, 'lang': 'ja', 'coordinates': None, 'possibly_sensitive': False, 'retweet_count': 44, 'like_count': 33, 'user_id': '1143349673995853824', 'user_screen_name': 'rizu_1122', 'user_name': '\ud83c\udfe1739\u3006\u308a\u305a\u3042\ud83d\udd2a\u4eca\u65e5\u25b6\u30b3\u30e9\u30dc\u9023\u6226', 'user_friends': 351, 'user_followers': 3572, 'user_location': '', 'user_verified': False, 'user_description': '\u50d5\u306e\u3070\u304b\ud83d\udc8d\u25b6@Ste11a_29 \ud83d\udc8d\u25b6@Ixx__17 \u5ac1\u304c\u623b\u308b\u307e\u3067\u754c\u9688\u53bb\u3089\u306a\u3044\u3088\u3002\u65e9\u304f\u623b\u3063\u3066\u304d\u3066\u25b6@Rey3222\u2665\u25b6@Sagiri_u3u                         \u30de\u30cd\u5148\u25b6@ruitya3 \n\ud83d\udc99\u25b6#\u308a\u305a\u3057\u3070\u5b9f\u7e3e', 'user_created_at': '2019-06-25T04:46:19', 'user_tweets': 9204, 'user_likes': 8087, 'user_lists': 4, 'user_image': 'https://pbs.twimg.com/profile_images/1356185388486852612/ksMmkZbF_normal.jpg', 'user_url': None, 'user_timestamp_utc': 1561430779.0, 'source_url': 'http://twitter.com/download/android', 'source_name': 'Twitter for Android'}]
    )
]


class TestUtils(object):
    def test_get_dates(self):
        for (date_str, tz), result in GET_DATES_TESTS:
            tz = timezone(tz)

            assert get_dates(date_str, locale=tz) == result, (date_str, tz)

    def test_prepare_tweet(self):
        tz = timezone('Europe/Paris')
        for tweet, correct_result in PREPARE_TWEET_TEST:
            result = prepare_tweet(tweet, locale=tz, id_key='_id')
            for sub_tweet, correct_sub_tweet in zip(result, correct_result):
                for key in correct_sub_tweet:
                    if key != 'collection_time':
                        assert sub_tweet[key] == correct_sub_tweet[key], 'Failed for key %s for tweet %s' % (key, correct_sub_tweet['id_str'])
