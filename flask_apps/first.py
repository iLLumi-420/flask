from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def hello_world():
    arg = request.args.get('arg')
    if arg:
        return f'<h2>Hello, {arg}!</h2>'
    else:
        return f'<h2>Hello, World!</h2>'