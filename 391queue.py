
from flask import Flask, request, redirect, url_for, render_template
from flask_socketio import SocketIO, emit
from collections import deque

app = Flask(__name__)
socketio = SocketIO(app)

queue = deque() 

SECRET_PASSWORD = "7N!N(~7oKJjE"
N_HELPED = "helpfile"
cur_helped = 0

def get_helped():
    with open(N_HELPED, "r") as f:
        return int(f.read())

def write_helped():
    global cur_helped
    cur_helped += 1
    with open(N_HELPED, "w") as f:
        f.write(str(cur_helped))

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def sync_queue():
    emit('queue_recv', {'data': list(queue)}, broadcast=True)

@socketio.on('queue_update', namespace='/')
def add_queue(message):
    entry = message['data'] 
    queue.append(entry)
    print(queue)
    emit('queue_recv', {'data': list(queue)}, broadcast=True)

@socketio.on('queue_dequeue', namespace='/')
def rm_queue(message):
    if message == SECRET_PASSWORD:
        if len(queue) > 0:
            queue.popleft()
            write_helped()
        emit('queue_recv', {'data': list(queue)}, broadcast=True)



if __name__ == "__main__":
    cur_helped = get_helped()
    socketio.run(app, host="0.0.0.0")
