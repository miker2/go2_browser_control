from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*") # Important for local development

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

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)