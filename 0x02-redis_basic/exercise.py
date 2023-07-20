#!/usr/bin/env python3
""" defines a class Cache"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """ decorator"""
    key = method.__qualname__

    @wraps(method)
    def increment(self, *args, **kwargs):
        """ increment count for the key in count_calls"""
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return increment


def call_history(method: Callable) -> Callable:
    """ Decorator"""
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        """ store input and output"""
        Input = str(args)
        q_name = method.__qualname__
        self._redis.rpush(q_name + ":inputs", Input)
        output = str(method(self, *args, **kwargs))
        self._redis.rpush(q_name + ":outputs", output)
        return output
    return wrapped


def replay(fn: Callable) -> None:
    """ Display the history of calls."""
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return

    in_key = '{}:inputs'.format(fn.__qualname__)
    out_key = '{}:outputs'.format(fn.__qualname__)

    fxn_call_count = 0
    if redis_store.exists(fn.__qualname__) != 0:
        fxn_call_count = int(redis_store.get(fn.__qualname__))

    print('{} was called {} times:'.format(fn.__qualname__, fxn_call_count))
    fxn_inputs = redis_store.lrange(in_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_inputs, fxn_outputs in zip(fxn_inputs, fxn_outputs):
        print('{}(*{})'.format(
            fn.__qualname__,
            fxn_inputs.decode('utf-8'),
            fxn_outputs
        ))


class Cache():
    """ stores an instance of the redis client"""
    def __init__(self):
        """ Constructor"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """" generate a random key using uuid"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self,
            key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        """ extract informtion saved in redis"""
        value = self._redis.get(key)
        if fn:
            value = fn(value)
        return value

    def get_str(self, key: str) -> str:
        """ Automatically parametrize Cache.get
            with the correct conversion function.
        """
        value = self._redis.get(key)
        return value.decode('UTF-8')

    def get_int(self, key: str) -> int:
        """ Parameterize cache from redis to string"""
        value = self._redis.get(key)
        try:
            value = int(value.decode('UTF-8'))
        except Exception:
            value = 0
        return value
