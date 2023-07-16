import requests
import time

def count_words(url):
    time.sleep(3)
    print('Job has been started')
    res = requests.get(url)
    words = res.text.split()
    word_count = len(words)
    return word_count
