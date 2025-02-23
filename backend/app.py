# import eventlet
# from eventlet import wsgi
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit

import os
import logging
import threading
import time

import asyncio
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '../frontend'))

# Enable logging and add a log handler to print to the console:
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


app = Flask(__name__,
            template_folder=os.path.join(FRONTEND_DIR, 'templates'),
            static_folder=os.path.join(FRONTEND_DIR, 'static'))
socketio = SocketIO(
    app,
    cors_allowed_origins="*", # Important for local development
    # async_mode='eventlet',
)

async def connect_to_robot(task_id, *args, **kwargs):
    print(f"+++++ connect_to_robot() called - {task_id=} .....")
    connected = False
    try:
        connection = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip="192.168.123.161")
        logging.info('Attempting to conect to robot...')

        print("+++++ debug 2.....")
        async with asyncio.timeout(15):  # Timeout after 30 seconds
            await connection.connect()

        print("+++++ connection attempt complete .....")
        connected = True
        # socketio.emit('connection_response', { 'connected': True }, room=task_id)
    except ValueError as e:
        print(f"===== Error: {e}")
        connected = False
        # socketio.emit('connection_response', { 'connected': False }, room=task_id)
    except asyncio.TimeoutError:
        print("===== Connection attempt timed out!")
        connected = False
    socketio.emit('connection_response', { 'connected': connected }, room=task_id)

@socketio.on('connect_webrtc')
def handle_connection(*args, **kwargs):
    task_id = session.get('task_id')
    if not task_id:
        task_id = str(time.time())
        session['task_id'] = task_id
    print(f"+++++ handle_connecion: task_id={task_id} +++++")

    asyncio.run(connect_to_robot(task_id, *args, **kwargs))
    # socketio.start_background_task(asyncio.to_thread, connect_to_robot, task_id, *args, **kwargs)

@socketio.on('joystick')
def handle_joystick(data):
    joystick = data['joystick']
    x = data['x']
    y = data['y']
    print(f"Joystick {joystick}: x={x}, y={y}")
    # ... robot control logic ...

@socketio.on('connect')
def handle_connect():
    task_id = session.get('task_id')
    if task_id:
        socketio.join_room(task_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control')
def control():
    return render_template('control.html')

@socketio.on("move")
def handle_move(data):
    print(f"Move joystick: X={data['x']}, Y={data['y']}")

@socketio.on("rotate")
def handle_rotate(data):
    print(f"Rotate joystick: X={data['x']}, Y={data['y']}")

@socketio.on("joystick_touch_start")
def handle_joystick_touch_start(data):
    print("joystick_touch_start", data)

@socketio.on("joystick_create")
def handle_joystick_create(data):
    print("joystick_create", data)

@socketio.on("joystick_destroy")
def handle_joystick_destroy(data):
    print("joystick_destroy", data)

@socketio.on('command')
def handle_command(command):
    print(f"Received command: {command}")
    # ... robot control logic ...

@socketio.on("action")
def handle_action(data):
    print("🔥 Action button pressed!" if data["pressed"] else "🔥 Action button released!")

@socketio.on("voice")
def handle_voice(data):
    print(f"🎤 Voice command received: {data['command'].lower()}")

@socketio.on("sit")
def handle_sit(data):
    if (data["pressed"]):
        print("🪑 Sit command received!")

@socketio.on("stand")
def handle_stand(data):
    if (data["pressed"]):
        print("📏 Stand command received!")

if __name__ == '__main__':
    # WSGIServer(app).run() # Use WSGIServer instead of app.run()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) # Use this for local testing only
    # app.run(host='0.0.0.0', port=5000, debug=True)
