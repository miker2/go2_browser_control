var socket = io();

let leftJoystick, rightJoystick;
let leftFeedback = document.getElementById('joystick-feedback-left');
let rightFeedback = document.getElementById('joystick-feedback-right');

function createJoystick(zone, event, side) {
    let touch = event.touches[0]; 
    let joystick = nipplejs.create({
        zone: zone,
        mode: 'dynamic',
        position: { left: touch.clientX + "px", top: touch.clientY + "px" },
        color: side === 'left' ? 'blue' : 'red'
    });

    let feedback = side === 'left' ? leftFeedback : rightFeedback;
    feedback.style.display = 'block';

    joystick.on('move', function(evt, data) {
        socket.emit(side === 'left' ? 'move' : 'rotate', { x: data.vector.x, y: data.vector.y });

        feedback.style.left = (touch.clientX + data.vector.x * 30) + "px";
        feedback.style.top = (touch.clientY + data.vector.y * 30) + "px";
    });

    joystick.on('end', function() {
        joystick.destroy();
        feedback.style.display = 'none';
    });

    return joystick;
}

document.getElementById('joystick-zone-left').addEventListener('touchstart', function(event) {
    if (!leftJoystick) leftJoystick = createJoystick(this, event, 'left');
}, { passive: false });

document.getElementById('joystick-zone-right').addEventListener('touchstart', function(event) {
    if (!rightJoystick) rightJoystick = createJoystick(this, event, 'right');
}, { passive: false });

// Button Events
document.getElementById('voice-button').addEventListener('click', function() {
    let recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    let button = this;
    button.classList.add("listening");
    recognition.start();

    recognition.onresult = function(event) {
        let command = event.results[0][0].transcript;
        socket.emit('voice', { command: command });
        button.classList.remove("listening");
    };

    recognition.onerror = function() {
        button.classList.remove("listening");
    };
});

function setupButton(buttonId, eventName) {
    let button = document.getElementById(buttonId);
    button.addEventListener('touchstart', function() {
        this.classList.add("active");
        socket.emit(eventName, { pressed: true });
    });

    button.addEventListener('touchend', function() {
        this.classList.remove("active");
        socket.emit(eventName, { pressed: false });
    });
}

setupButton('action-button', 'action');
setupButton('sit-button', 'sit');
setupButton('stand-button', 'stand');