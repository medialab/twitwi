TWEET_FIELDS = {
    'attachments',
    'author_id',
    'context_annotations',
    'conversation_id',
    'created_at',
    'entities',
    'geo',
    'id',
    'in_reply_to_user_id',
    'lang',
    'possibly_sensitive',
    'public_metrics',
    'referenced_tweets',
    'reply_settings',
    'source',
    'text',
    'withheld'
}

MEDIA_FIELDS = {
    'media_key',
    'type',
    'duration_ms',
    'height',
    'preview_image_url',
    'public_metrics',
    'width',
    'alt_text'
}

POLL_FIELDS = {
    'id',
    'options',
    'duration_minutes',
    'end_datetime',
    'voting_status'
}

PLACE_FIELDS = {
    'full_name',
    'id',
    'contained_within',
    'country',
    'country_code',
    'geo',
    'name',
    'place_type'
}

USER_FIELDS = {
    'id',
    'name',
    'username',
    'created_at',
    'description',
    'entities',
    'location',
    'pinned_tweet_id',
    'profile_image_url',
    'protected',
    'public_metrics',
    'url',
    'verified',
    'withheld'
}

TWEET_EXPANSIONS = {
    'author_id',
    'referenced_tweets.id',
    'in_reply_to_user_id',
    'attachments.media_keys',
    'attachments.poll_ids',
    'geo.place_id',
    'entities.mentions.username',
    'referenced_tweets.id.author_id'
}

TWEET_PARAMS = {
    'tweet.fields': ','.join(field for field in TWEET_FIELDS),
    'media.fields': ','.join(field for field in MEDIA_FIELDS),
    'poll.fields': ','.join(field for field in POLL_FIELDS),
    'place.fields': ','.join(field for field in PLACE_FIELDS),
    'user.fields': ','.join(field for field in USER_FIELDS)
}

USER_EXPANSIONS = {
    'pinned_tweet_id'
}

USER_PARAMS = {
    'user.fields': ','.join(field for field in USER_FIELDS),
    'tweet.fields': ','.join(field for field in TWEET_FIELDS)
}

# Lists

LIST_FIELDS = {
    'created_at',
    'follower_count',
    'member_count',
    'private',
    'description',
    'owner_id'
}

LIST_EXPANSIONS = 'owner_id'

LIST_PARAMS = {
    'list.fields': ','.join(field for field in LIST_FIELDS),
    'user.fields': ','.join(field for field in USER_FIELDS)
}

LIST_TWEETS_EXPANSIONS = 'author_id'

LIST_MEMBERS_EXPANSIONS = 'pinned_tweet_id'

LIST_TWEETS_OR_MEMBERS_PARAMS = {
    'tweet.fields': ','.join(field for field in TWEET_FIELDS),
    'user.fields': ','.join(field for field in USER_FIELDS)
}

APP_ONLY_ROUTES = {
    'tweets/counts/recent',
    'tweets/counts/all',
    'tweets/search/all'
}
