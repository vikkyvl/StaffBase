import redis

class Redis:
    def __init__(self, host='redis-13066.c124.us-central1-1.gce.redns.redis-cloud.com', port=13066, username="default", password="5i0VNFZWaNcR9oPNzHdrO2ZSPKHUDdXe"):
        self._connection = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
            username=username,
            password=password
        )


