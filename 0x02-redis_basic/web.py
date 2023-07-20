#!/usr/bin/env python3
""" Implementing an expiring web cache and tracker
    obtain the HTML content of a particular URL and returns it """
import requests
import redis
import time

redis_client = redis.Redis()

def expiration_time():
    return int(time.time()) + 10  # Set the cache expiration time to 10 seconds

def get_page(url: str) -> str:
    key = f"count:{url}"
    
    # Check if the URL's content is already cached in Redis
    cached_content = redis_client.get(url)
    if cached_content:
        # Increment the access count for this URL
        redis_client.incr(key)
        return cached_content.decode('utf-8')
    
    # If not cached, fetch the content using requests
    response = requests.get(url)
    content = response.text
    
    # Cache the content in Redis with an expiration time
    redis_client.setex(url, expiration_time(), content)
    
    # Initialize the access count if not present
    if not redis_client.exists(key):
        redis_client.set(key, 1)
    else:
        # Increment the access count for this URL
        redis_client.incr(key)
    
    return content
