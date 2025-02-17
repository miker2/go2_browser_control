from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flup.server.fcgi import WSGIServer

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '../frontend'))

app = Flask(__name__
            template_folder=os.path.join(FRONTEND_DIR, 'templates'),
            static_folder=os.path.join(FRONTEND_DIR, 'static'))
socketio = SocketIO(app, async_mode="eventlet") # Important for local development

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('joystick')
def handle_joystick(data):
    joystick = data['joystick']
    x = data['x']
    y = data['y']
    print(f"Joystick {joystick}: x={x}, y={y}")
    # ... robot control logic ...

@socketio.on('command')
def handle_command(command):
    print(f"Received command: {command}")
    # ... robot control logic ...

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on("move")
def handle_move(data):
    print(f"Move joystick: X={data['x']}, Y={data['y']}")

@socketio.on("rotate")
def handle_rotate(data):
    print(f"Rotate joystick: X={data['x']}, Y={data['y']}")

@socketio.on("action")
def handle_action(data):
    print("🔥 Action button pressed!" if data["pressed"] else "🔥 Action button released!")

@socketio.on("voice")
def handle_voice(data):
    print(f"🎤 Voice command received: {data['command']}")

@socketio.on("sit")
def handle_sit(data):
    print("🪑 Sit command received!")

@socketio.on("stand")
def handle_stand(data):
    print("📏 Stand command received!")

if __name__ == '__main__':
    WSGIServer(app).run() # Use WSGIServer instead of app.run()
    # socketio.run(app, debug=True, host='0.0.0.0', port=5000) # Use this for local testing only
