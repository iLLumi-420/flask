from flask import Flask, request, session
from redis import Redis

app = Flask(__name__)
app.secret_key = 'secret_key'

redis = Redis()

@app.route("/")
def hello_world():
    arg = request.args.get('arg')
    if arg:
        return f'<h2>Hello, {arg}!</h2>'
    else:
        return f'''
                <h2>Hello, World!</h2>
                <a href='/count'>Count Page</a>
        '''
    
@app.route('/count')
def count():
    session['visit_count'] = session.get('visit_count', 0) + 1
    return f'''
            Total visit: {session["visit_count"]}
            <a href='/'>Home</a>
    '''

