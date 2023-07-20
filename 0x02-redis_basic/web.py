#!/usr/bin/env python3
""" Implementing an expiring web cache and tracker
    obtain the HTML content of a particular URL and returns it """
import redis
import requests


redi = redis.Redis()
count = 0


def get_page(url: str) -> str:
    """ Impelements core function of get page which is accessed."""
     """ Check if the URL's content is already cached in Redis.""""
    cached_content = redi.get(url)
    if cached_content:
        """" Increment the access count for this URL """
        redi.incr(f"count:{url}")
        return cached_content.decode('utf-8')
        
    redi.set(f"cached:{url}", count)
    response = requests.get(url)
    redi.incr(f"count:{url}")
    redi.setex(f"cached:{url}", 10, redi.get(f"cached:{url}"))
    return response.text


if __name__ == "__main__":
    get_page('http://slowwly.robertomurray.co.uk')
