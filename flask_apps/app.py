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
def home():
    if 'user' not in session:
        session['user'] = 'user_' + str(redis.incr('user_count'))

    urls_key = f'urls_{session["user"]}'
    jobs_key = f'job_id_{session["user"]}'

    if request.method == 'POST':
        url = request.form['url']
        redis.rpush(urls_key, url)
        flash('URL has been saved')
        job = queue.enqueue(count_words, url)

        # Store the job ID with the user
        redis.rpush(jobs_key, job.id)

    user_urls = redis.lrange(urls_key, 0, -1)
    job_ids = redis.lrange(jobs_key, 0, -1)
    data = zip(user_urls, job_ids)

    return render_template('index.html', data=data)

    
   


def check_job_status(job_id):
    redis_conn = Redis()
    job = Job.fetch(job_id, connection=redis_conn)
    if job.is_finished:
        word_count = job.result
        redis_conn.set('word_count_{job.id}', word_count)
        return f'<p>Job is finished. Word count: {word_count}</p>'
    else:
        return '<p>Job is still running. Please check again later.</p>'


@app.route('/result/<job_id>')
def get_job_result(job_id):
    # Check if the job belongs to the current user
    user = session.get('user')
    job_id_saved = redis.lrange(f'job_id_{user}',0,-1)
    job_id_decoded = [id.decode('utf-8') for id in job_id_saved]

    
    print(job_id_saved)
    print(job_id)

    if job_id in job_id_decoded:
        result = check_job_status(job_id)
        return f'<p>{result}</p>'
    else:
        return '<p>You do not have permission to access this job result.</p>'



if __name__ == '__main__':
    app.run(debug=True)
