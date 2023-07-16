from redis import Redis
from rq import Worker, Queue, Connection
from flask_apps.worker_functions import count_words

redis = Redis()
queue = Queue(connection=redis)

if __name__ == '__main__':
    with Connection(connection=redis):
        worker = Worker(queue)
        worker.work()