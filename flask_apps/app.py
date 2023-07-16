from flask import Flask, request
from redis import Redis
from rq import Queue
from rq.job import Job
from flask_apps.worker_functions import count_words


app = Flask(__name__)
app.secret_key = 'secret_key'

redis = Redis()
queue = Queue(connection=redis)



@app.route('/')
def hello_world():
    arg = request.args.get('arg')
    if arg:
        return f'<h2>Hello, {arg}!</h2>'
    else:
        return '''
                <h2>Hello, World!</h2>
                <a href='/count'>Count Page</a>
                <a href='/process'>Process Page</a>
        '''

@app.route('/count')
def count():
    count = redis.incr('visit_count')
    name = redis.get('name')
    return f'''
            Total visit: {count}<br>
            {name}
            <a href='/'>Home</a>
    '''

def check_job_status(job_id):
    redis_conn = Redis()
    job = Job.fetch(job_id, connection=redis_conn)
    if job.is_finished:
        word_count = job.result
        redis_conn.set('word_count', word_count)
        return f'<p>Job is finished. Word count: {word_count}</p>'
    else:
        return '<p>Job is still running. Please check again later.</p>'

@app.route('/process')
def process():
    job = queue.enqueue(count_words, 'https://tihalt.com/examples-of-static-websites/')
    job_id = job.get_id()
    return f'''
        <p>Job is enqueued at job id: {job_id}</p>
        <a href="/result/{job_id}">Check result</a>
        <a href="/">Home</a>
    '''
    
@app.route('/result/<job_id>')
def get_job_result(job_id):
    result = check_job_status(job_id)
    return f'<p>{result}</p>'

if __name__ == '__main__':
    app.run(debug=True)
