# import eventlet
# from eventlet import wsgi
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '../frontend'))

app = Flask(__name__,
            template_folder=os.path.join(FRONTEND_DIR, 'templates'),
            static_folder=os.path.join(FRONTEND_DIR, 'static'))
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", # Important for local development
    async_mode='eventlet', 
)

@socketio.on('connect-to-robot')
def handle_connect(data):
    print('Client connected')
    # Execute the code here to connect to the WebRTC client and
    # Display info to the user during the connection process.
    # Once the connection is established, send a message to the client
    # and render the control.html template.

    emit('render_response', { 'data': "connection info here!" })

@socketio.on('joystick')
def handle_joystick(data):
    joystick = data['joystick']
    x = data['x']
    y = data['y']
    print(f"Joystick {joystick}: x={x}, y={y}")
    # ... robot control logic ...

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
