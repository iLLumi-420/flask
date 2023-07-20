import requests
import time
from redis import Redis
from rq import Queue

redis = Redis()
queue = Queue(connection=redis)


def count_words(url):
    time.sleep(15)
    print('Job has been started')
    try:
        res = requests.get(url)
        words = res.text.split()
        word_count = len(words)
        redis.set(f'word_count_{url}', word_count)
        return word_count
    except:
        redis.set(f'word_count_{url}', 'Invalid url')
        return 'Invalid url'
