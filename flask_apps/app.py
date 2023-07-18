from flask import Flask, request, render_template, session,flash
from flask_apps.worker_functions import count_words
from redis import Redis
from rq import Queue
from rq.job import Job
from auth import auth_bp, login_required

app = Flask(__name__)
app.secret_key = 'secret_key'

redis = Redis()
queue = Queue(connection=redis)


app.register_blueprint(auth_bp)

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
@login_required
def home():
    user = session['user']
    key = f'urls_{user}'

    if request.method == 'POST':
        url = request.form['url']
        redis.rpush(key, url)
        flash('URL has been saved')
        job = queue.enqueue(count_words, url)
        redis.set(f'job_id_{url}', job.id)



    user_urls = redis.lrange(key,0, -1) 
    print(user_urls) 

    job_ids = []
    for url in user_urls:
        job_id = redis.get(f'job_id_{url.decode("utf-8")}').decode('utf-8')
        print(job_id)
        job_ids.append(job_id)
    

    data = zip(user_urls, job_ids)
    
    return render_template('index.html', data=data)
    
   


def check_job_status(job_id):
    redis_conn = Redis()
    job = Job.fetch(job_id, connection=redis_conn)
    if job.is_finished:
        word_count = job.result
        redis_conn.set('word_count', word_count)
        return f'<p>Job is finished. Word count: {word_count}</p>'
    else:
        return '<p>Job is still running. Please check again later.</p>'


@app.route('/result/<job_id>')
@login_required
def get_job_result(job_id):
    result = check_job_status(job_id)
    return f'<p>{result}</p>'

if __name__ == '__main__':
    app.run(debug=True)
