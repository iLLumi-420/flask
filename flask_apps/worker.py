from redis import Redis
from rq import Worker, Queue, Connection
import worker_functions

redis = Redis()
queue = Queue(connection=redis)

if __name__ == '__main__':
    with Connection(connection=redis):
        worker = Worker(queue)
        worker.work()