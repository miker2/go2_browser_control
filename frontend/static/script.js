var socket = io();

let leftJoystick, rightJoystick;
let leftFeedback = document.getElementById('joystick-feedback-left');
let rightFeedback = document.getElementById('joystick-feedback-right');

function createJoystick(zone, event, side) {
    if (event.touches.length === 0) {
        console.error("No touches found in event");
        return null;
    }

    let touch = event.touches[0]; 
    let joystick = nipplejs.create({
        zone: zone,
        mode: 'dynamic',
        position: { left: touch.clientX + "px", top: "-" + touch.clientY + "px" },
        color: side === 'left' ? 'blue' : 'red'
    });
    if (!joystick) {
        console.error("Failed to create joystick");
        return null;
    }

    socket.emit("joystick_create", { side: side, zone: zone, position: {left: touch.clientX, top: touch.clientY} })

    // let feedback = side === 'left' ? leftFeedback : rightFeedback;
    // feedback.style.display = 'block';

    joystick.on('move', function(evt, data) {
        socket.emit(side === 'left' ? 'move' : 'rotate', { x: data.vector.x, y: data.vector.y });

        // feedback.style.left = (touch.clientX + data.vector.x * 30) + "px";
        // feedback.style.top = (touch.clientY + data.vector.y * 30) + "px";
    });

    joystick.on('end', function() {
        joystick.destroy();
        joystick = null;
        if (side === 'left') leftJoystick = null;
        else rightJoystick = null;
        // feedback.style.display = 'none';
        socket.emit("joystick_destroy", { side: side, zone: zone, joystick: !!joystick })

    });

    return joystick;
}

document.getElementById('joystick-zone-left').addEventListener('touchstart', function(event) {
    socket.emit("joystick_active", { active: true, side: "left", 
        joystick_exists: !!leftJoystick, 
        x: event.touches[0].clientX, y: event.touches[0].clientY });
    if (!leftJoystick) leftJoystick = createJoystick(this, event, 'left');
}, { passive: false });

document.getElementById('joystick-zone-right').addEventListener('touchstart', function(event) {
    socket.emit("joystick_active", { active: true, side: "right", 
        joystick_exists: !!leftJoystick, 
        x: event.touches[0].clientX, y: event.touches[0].clientY });
    if (!rightJoystick) rightJoystick = createJoystick(this, event, 'right');
}, { passive: false });

document.getElementById('joystick-zone-right').addEventListener('touchend', function(event) {
    socket.emit("joystick_destroy", { side: "right", joystick: !!rightJoystick });
});

// Button Events
var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
var recognition = new SpeechRecognition();

if (!SpeechRecognition) {
    alert("Voice input is not supported on this device/browser.");
} else {
    recognition.continous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
}

document.getElementById('voice-button').addEventListener('click', function() {
    let button = this;
    button.classList.add("listening");
    console.log('Listening...');
    recognition.start();

    recognition.onresult = function(event) {
        let command = event.results[0][0].transcript;
        console.log('Voice Command:', command);
        socket.emit('voice', { command: command });
        button.classList.remove("listening");
    };

    recognition.onerror = function() {
        button.classList.remove("listening");
        alert('Voice recognition error: ' + event.error);
    };

    recognition.onend = function() {
        button.classList.remove("listening");
    };
});

function setupButton(buttonId, eventName) {
    let button = document.getElementById(buttonId);
    button.addEventListener('touchstart', function() {
        this.classList.add("active");
        console.log(eventName, 'pressed');
        socket.emit(eventName, { pressed: true });
    });

    button.addEventListener('touchend', function() {
        this.classList.remove("active");
        console.log(eventName, 'released');
        socket.emit(eventName, { pressed: false });
    });
}

setupButton('action-button', 'action');
setupButton('sit-button', 'sit');
setupButton('stand-button', 'stand');