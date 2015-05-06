#coding:utf-8

###
### cache请求的html
###

from tornado.web import RequestHandler
import redis


def getRedisObj(rdb=0):
    pool = redis.ConnectionPool(
            host='127.0.0.1', password='', port=6379, db=rdb, socket_timeout=3)
    r = redis.Redis(connection_pool=pool)
    return r


class RedisCacheHandler(RequestHandler):

    ttl = 60 # 缓存的的时间
    has_cache_in_redis = False
    check_can_cache_result = True

    def chech_can_cache(self):

        return True

    def prepare(self):

        super(RedisCacheHandler, self).prepare()
        self.check_can_cache_result = self.chech_can_cache()
        if self.check_can_cache_result is False:
            return
        r = getRedisObj()
        cache_key = self.gen_cache_key()
        html = r.get(cache_key)
        if html:
            self.has_cache_in_redis = True
            self.finish(html)

    def flush(self, include_footers=False, callback=None):

        if self._status_code != 200:
            #http code 为200 的才缓存
            pass
        elif self.has_cache_in_redis is True or self.check_can_cache_result is False:
            # 已经缓存或者不需要缓存
            pass
        else:
            html = ''.join(self._write_buffer)
            r = getRedisObj()
            cache_key = self.gen_cache_key()
            r.set(cache_key, html)
            r.expire(cache_key, self.ttl)
        return super(RedisCacheHandler, self).flush(include_footers=include_footers, callback=callback)

    def gen_cache_key(self):
        # 生成 redis key
        return self.request.path

    def define_prepare(self):
        # 每次请求都要执行的代码 放这里
        pass