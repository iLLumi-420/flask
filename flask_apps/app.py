from flask import Flask, request, render_template, redirect, url_for, session
from flask_apps.worker_functions import count_words
from redis import Redis
from rq import Queue
from rq.job import Job

app = Flask(__name__)
app.secret_key = 'secret_key'

redis = Redis()
queue = Queue(connection=redis)


@app.route('/signup', methods=['GET', 'POST'])
def signup_user():

    if request.method == 'POST':
    
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        if not username or not password or not confirm:
                error_message = 'Please fill out all the required fields.'
                return render_template('signup.html', error_message=error_message)

        if password != confirm:
            error_message = 'Password and confirm do not match. Please try again.'
            return render_template('signup.html', error_message=error_message)

        if redis.hexists('users', username):
            error_message = 'User name already taken'
            return render_template('signup.html', error_message=error_message)
        
        redis.hset('users', username, password)
        return redirect(url_for('login_user'))

    return render_template('signup.html')

        
@app.route('/login', methods = ['GET','POST'])
def login_user():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not redis.hexists('users', username):
            error_message = 'Incorrect usename or password'
            return render_template('login.html', error_message=error_message)
        
        stored_password = redis.hget('users', username).decode('utf-8')

        if stored_password != password:
            print(password)
            print(stored_password)
            error_message = 'Incorrect username or password'
            return render_template('login.html', error_message=error_message)
        
        session['user'] = username
        print('redirecting to home')
        return redirect(url_for('home'))

    return render_template('login.html')    



@app.route('/')
def home():
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
