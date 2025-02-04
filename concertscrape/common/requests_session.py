import requests
import time

class RateLimitedRequestsSession(requests.Session):
    def __init__(self, rate_limit_enabled=True, delay=1.0):
        super().__init__()
        self.last_request_time = 0
        self.rate_limit_enabled = rate_limit_enabled
        self.delay = delay

    def request(self, *args, **kwargs):
        if self.rate_limit_enabled:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
        
        response = super().request(*args, **kwargs)
        self.last_request_time = time.time()
        return response

REQUESTS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0"
}
