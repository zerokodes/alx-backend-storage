#!/usr/bin/env python3
""" Implementing an expiring web cache and tracker
    obtain the HTML content of a particular URL and returns it """
import requests
import time
import functools

# A dictionary to store the cached results and access counts
cache = {}

def expiration_time():
    return int(time.time()) + 10  # Set the cache expiration time to 10 seconds

def cache_decorator(func):
    @functools.wraps(func)
    def wrapper(url):
        key = f"count:{url}"
        # Check if the URL is already cached
        if url in cache and cache[url]["expiration"] > time.time():
            cache[key]["count"] += 1
            return cache[url]["content"]
        # If not cached or expired, fetch the content and cache it
        response = requests.get(url)
        content = response.text
        cache[url] = {"content": content, "expiration": expiration_time()}
        # Initialize the access count if not present
        if key not in cache:
            cache[key] = {"count": 1}
        else:
            cache[key]["count"] += 1
        return content
    return wrapper

@cache_decorator
def get_page(url: str) -> str:
    response = requests.get(url)
    return response.text
