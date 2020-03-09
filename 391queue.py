
from flask import Flask, request, redirect, url_for, render_template
from flask_socketio import SocketIO, emit
from collections import deque


import datetime, json

app = Flask(__name__)
socketio = SocketIO(app)

queue = deque() 
active_people = set()
N_HELPED = "dayfile"

def get_helped():
    with open(N_HELPED, "r") as f:
        return json.loads(f.read()) 

help_days = get_helped()

SECRET_PASSWORD = "ece391"
admins = set() # session ids

cur_helped = 0
today = datetime.datetime.today().strftime('%d-%m-%Y')

def write_helped():
    global cur_helped, help_days, today
    today = datetime.datetime.today().strftime('%d-%m-%Y')
    if today not in help_days:
        help_days[today] = 0
        cur_helped = 0
    cur_helped += 1
    help_days[today] = cur_helped
    with open(N_HELPED, "w") as f:
        json.dump(help_days, f)


def admin_broadcast():
    for admin in admins:
        emit('admin_push', {'data' : len(queue)}, room=admin)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def sync_queue():
    emit('queue_recv', {'data': list(queue)}, broadcast=True)

@socketio.on('queue_update', namespace='/')
def add_queue(message):
    global active_people
    entry = message['data']
    print(request.sid) 
    if entry not in active_people:
        queue.append(entry)
        active_people.add(entry)
    
    if len(admins) > 0:
        admin_broadcast()

    print(queue)
    emit('queue_recv', {'data': list(queue)}, broadcast=True)

@socketio.on('queue_dequeue', namespace='/')
def rm_queue(message):
    global admins
    if message == SECRET_PASSWORD:
        if len(queue) > 0:
            active_people.remove(queue.popleft())
            write_helped()
            if request.sid not in admins:
                admins.add(str(request.sid))
            print(admins)
            admin_broadcast()  
            
        emit('queue_recv', {'data': list(queue)}, broadcast=True)



if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
