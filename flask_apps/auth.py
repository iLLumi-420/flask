from flask import Blueprint, request, render_template, redirect, url_for, session
from redis import Redis

auth_bp = Blueprint('auth', __name__)
redis = Redis()

@auth_bp.route('/signup', methods=['GET', 'POST'])
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
        return redirect(url_for('auth.login_user'))

    return render_template('signup.html')

        
@auth_bp.route('/login', methods = ['GET','POST'])
def login_user():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not redis.hexists('users', username):
            error_message = 'Incorrect usename or password'
            return render_template('login.html', error_message=error_message)
        
        stored_password = redis.hget('users', username).decode('utf-8')

        if stored_password != password:
            error_message = 'Incorrect username or password'
            return render_template('login.html', error_message=error_message)
        
        session['user'] = username
        print('redirecting to home')
        return redirect(url_for('home'))

    return render_template('login.html')   


@auth_bp.route('/logout')
def logout_user():
    session.pop('user', None)
    return redirect(url_for('home'))