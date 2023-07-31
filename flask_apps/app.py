from flask import Flask, request, render_template, session, flash
from worker_functions import count_words
from redis import Redis
from rq import Queue
from rq.job import Job
import hashlib


app = Flask(__name__)
app.secret_key = 'secret_key'

redis = Redis(host='redis', port=6379)
queue = Queue(connection=redis)

# app.register_blueprint(auth_bp)


def hash(url):
    url_bytes = url.encode('utf-8')    
    sha256_hash = hashlib.sha256(url_bytes).hexdigest()    
    return sha256_hash[:24]

@app.route('/count')
def count():
    count = redis.incr('visit_count')
    name = redis.get('name')
    return f'''
            Total visit: {count}<br>
            {name}
            <a href='/'>Home</a>
    '''

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user' not in session:
        session['user'] = 'user_' + str(redis.incr('user_count'))
    
    urls_key = f'urls_{session["user"]}'

    if request.method == 'POST':
        url = request.form['url']
        hashed_url = hash(url)
        redis.rpush(urls_key, url)
        flash('URL has been saved')
        job = queue.enqueue(count_words, url, job_id=hashed_url)

    
    user_urls = redis.lrange(urls_key,0,-1)
    job_ids = [hash(url.decode('utf-8')) for url in user_urls]

    data = zip(user_urls, job_ids)
      
    return render_template('index.html', data=data)

def check_job_status(job_id):
    redis_conn = Redis(host='redis', port=6379)
    job = Job.fetch(job_id, connection=redis_conn)
    if job.is_finished:
        word_count = job.result
        redis_conn.set('word_count_{job.id}', word_count)
        word_count = redis.get('word_count_{job.id}').decode('utf-8')
        return f'<p>Job is finished. Word count: {word_count}</p>'
    else:
        return '<p>Job is still running. Please check again later.</p>'

@app.route('/result/<job_id>')
def get_job_result(job_id):
    user = session['user']
    user_urls = redis.lrange(f'urls_{user}',0,-1)
    hash_urls = [hash(url.decode('utf-8')) for url in user_urls]

    if job_id not in hash_urls:
        return 'You are not authrized to view this data'
    result = check_job_status(job_id)
    return f'<p>{result}</p>'
         


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
