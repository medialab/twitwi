# =============================================================================
# Twitwi Client Wrapper
# =============================================================================
#
# Wrapper for the `twitter` library API client able to rotate the two possible
# endpoints to maximize throughput.
#
import json
import time
from operator import itemgetter
from twitter import Twitter, OAuth, OAuth2, TwitterHTTPError

from twitwi.exceptions import TwitterWrapperMaxAttemptsExceeded

DEFAULT_MAX_ATTEMPTS = 5


class TwitterWrapper(object):

    def __init__(self, token, token_secret, consumer_key, consumer_secret,
                 listener=None):
        self.oauth = OAuth(
            token,
            token_secret,
            consumer_key,
            consumer_secret
        )

        bearer_token_client = Twitter(
            api_version=None,
            format='',
            secure=True,
            auth=OAuth2(consumer_key, consumer_secret)
        )

        bearer_token = json.loads(
            bearer_token_client.oauth2.token(grant_type='client_credentials')
        )['access_token']

        self.oauth2 = OAuth2(bearer_token, consumer_key, consumer_secret)

        self.endpoints = {
            'user': Twitter(auth=self.oauth),
            'app': Twitter(auth=self.oauth2)
        }

        self.waits = {}
        self.auth = {}

        self.listener = listener

    def call(self, route, max_attempts=DEFAULT_MAX_ATTEMPTS, **kwargs):
        attempts = 0

        while attempts < max_attempts:

            if route not in self.auth:
                self.auth[route] = 'user'

            auth = self.auth[route]

            try:
                return self.api[auth].__getattr__('/'.join(route))(**kwargs)

            except TwitterHTTPError as e:

                # Rate limited
                if e.e.code == 429:
                    now = time()
                    reset = int(e.e.headers['X-Rate-Limit-Reset'])

                    if route not in self.waits:
                        self.waits[route] = {'user': now, 'app': now}

                    self.waits[route][auth] = reset

                    if callable(self.listener):
                        self.listener('rate-limited', {
                            'route': route,
                            'kwargs': kwargs,
                            'reset': reset,
                            'auth': auth
                        })

                    min_wait = min(self.waits[route].items(), key=itemgetter(1))

                    if min_wait[1] > now:
                        sleeptime = 5 + max(0, int(min_wait[1] - now))

                        if callable(self.listener):
                            self.listener('waiting', {
                                'auth': min_wait[0],
                                'reset': min_wait[1],
                                'sleep': sleeptime
                            })

                        time.sleep(sleeptime)

                    self.auth[route] = min_wait[0]

                    continue

                # Different error
                else:
                    attempts += 1

        raise TwitterWrapperMaxAttemptsExceeded
