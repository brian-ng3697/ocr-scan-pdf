import redis

class RedisDB:
    def __call__(self):
        self.ri = self.redisInstance()
        pass

    def redisInstance(self):
        # try:
            # r = redis.StrictRedis(decode_responses=True, host='localhost', port=6379, db=0, password="sOmE_sEcUrE_pAsS", socket_timeout=None)
            r = redis.StrictRedis(decode_responses=True, host='192.168.68.114', port=6379, db=0, password="", socket_timeout=None)
            return r
            # yield r
        # finally:
        #     r.close()

# def redisInstance():
#     try:
#         r = redis.StrictRedis(decode_responses=True, host='localhost', port=6379, db=0, password="sOmE_sEcUrE_pAsS", socket_timeout=None)
#         return r
#     finally:
#         r.close()