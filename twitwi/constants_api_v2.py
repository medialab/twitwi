TWEETS_LOOKUP_PARAMS = {
    'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld',
    'media.fields': 'media_key,type,duration_ms,height,preview_image_url,public_metrics,width,alt_text',
    'poll.fields': 'id,options,duration_minutes,end_datetime,voting_status',
    'place.fields': 'full_name,id,contained_within,country,country_code,geo,name,place_type',
    'user.fields': 'id,name,username,created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld'
}

TWEETS_LOOKUP_EXPANSIONS = 'author_id,referenced_tweets.id,in_reply_to_user_id,attachments.media_keys,attachments.poll_ids,geo.place_id,entities.mentions.username,referenced_tweets.id.author_id'

USER_TWEET_OR_MENTION_TIMELINE_EXPANSIONS = 'attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id'

USER_TWEET_OR_MENTION_TIMELINE_PARAMS = {
    'media.fields': 'duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics,alt_text',
    'poll.fields': 'id,options,duration_minutes,end_datetime,voting_status',
    'place.fields': 'full_name,id,contained_within,country,country_code,geo,name,place_type',
    'user.fields': 'id,name,username,created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld',
    'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld'
}

SEARCH_TWEETS_EXPANSIONS = 'attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id'

SEARCH_TWEETS_PARAMS = {
    'media.fields': 'duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics,alt_text',
    'poll.fields': 'id,options,duration_minutes,end_datetime,voting_status',
    'place.fields': 'full_name,id,contained_within,country,country_code,geo,name,place_type',
    'user.fields': 'id,name,username,created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld',
    'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld'
}

# only the last 100 retweeters
RETWEETERS_EXPANSIONS = 'pinned_tweet_id'

RETWEETERS_PARAMS = {
    'user.fields': 'id,name,username,created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld',
    'media.fields': 'duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics,alt_text',
    'poll.fields': 'id,options,duration_minutes,end_datetime,voting_status',
    'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld',
    'place.fields': 'full_name,id,contained_within,country,country_code,geo,name,place_type'
}

LIKED_BY_USERS_EXPANSIONS = 'pinned_tweet_id'

LIKED_BY_USERS_PARAMS = {
    'user.fields': 'id,name,username,created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld',
    'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld',
    'media.fields': 'duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics,alt_text',
    'poll.fields': 'id,options,duration_minutes,end_datetime,voting_status',
    'place.fields': 'full_name,id,contained_within,country,country_code,geo,name,place_type'
}

LIKED_TWEETS_EXPANSIONS = 'attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id'

LIKED_TWEETS_PARAMS = {
    'user.fields': 'id,name,username,created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld',
    'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld',
    'media.fields': 'duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics,alt_text',
    'poll.fields': 'id,options,duration_minutes,end_datetime,voting_status',
    'place.fields': 'full_name,id,contained_within,country,country_code,geo,name,place_type'
}

USERS_LOOKUP_EXPANSIONS = 'pinned_tweet_id'

USERS_LOOKUP_PARAMS = {
    'user.fields': 'id,name,username,created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld',
    'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld'
}

FOLLOWING_OR_FOLLOWERS_EXPANSIONS = 'pinned_tweet_id'

FOLLOWING_OR_FOLLOWERS_PARAMS = {
    'user.fields': 'id,name,username,created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld',
    'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld'
}

# Lists

LIST_LOOKUP_EXPANSIONS = 'owner_id'

LIST_LOOKUP_PARAMS = {
    'list.fields': 'created_at,follower_count,member_count,private,description,owner_id',
    'user.fields': 'id,name,username,created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld'
}

OWNED_LISTS_EXPANSIONS = 'owner_id'

OWNED_LISTS_PARAMS = {
    'list.fields': 'created_at,follower_count,member_count,private,description,owner_id',
    'user.fields': 'id,name,username,created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld'
}

LIST_TWEETS_EXPANSIONS = 'author_id'

LIST_TWEETS_OR_MEMBERS_PARAMS = {
    'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld',
    'user.fields': 'id,name,username,created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld'
}

LIST_MEMBERS_EXPANSIONS = 'pinned_tweet_id'

APP_ONLY_ROUTES = {
    'tweets/counts/recent',
    'tweets/counts/all',
    'tweets/search/all'
}
