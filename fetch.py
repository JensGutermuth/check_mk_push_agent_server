# -*- coding: utf-8 -*-

import sys

from redis import StrictRedis

redis = StrictRedis()

if __name__ == '__main__':
    assert len(sys.argv) == 2
    hostname = sys.argv[1]
    redis_key = ':'.join(['check_mk_push_agent', 'data', hostname])
    data = redis.get(redis_key)
    assert data is not None
    assert redis.delete(redis_key) == 1
    print data
