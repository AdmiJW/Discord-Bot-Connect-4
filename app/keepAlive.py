from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
	return "Hello World"

def start_server():
	app.run(host='0.0.0.0', port=8080)

def keep_alive():
	t = Thread(target=start_server)
	t.start()
