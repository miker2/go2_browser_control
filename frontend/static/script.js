var socket = io();

let leftFeedback = document.getElementById('joystick-feedback-left');
let rightFeedback = document.getElementById('joystick-feedback-right');

// Create left joystick
var leftJoystick = nipplejs.create({
    zone: document.getElementById('joystick-zone-left'),
    color: 'blue',
    mode: 'dynamic'
});

// Listen for move events on left joystick
leftJoystick.on('move', function(evt, data) {
    console.log("Left Joystick Move", data);
    socket.emit('move', { x: data.vector.x, y: data.vector.y });

    leftFeedback.style.display = 'block';
    leftFeedback.style.left = ( data.clientX + data.vector.x * 30) + "px";
    leftFeedback.style.top = ( data.clientY + data.vector.y * 30) + "px";
});

leftJoystick.on('end', function() {
    socket.emit("joystick_destroy", { side: "left" })
    leftFeedback.style.display = 'none';
});

// Create right joystick
var rightJoystick = nipplejs.create({
    zone: document.getElementById('joystick-zone-right'),
    color: 'red',
    mode: 'dynamic'
});

// Listen for move events on right joystick
rightJoystick.on('move', function(evt, data) {
    console.log("Right Joystick Move", data);
    socket.emit('rotate', { x: data.vector.x, y: data.vector.y });

    rightFeedback.style.display = 'block';
    rightFeedback.style.left = ( data.clientX + data.vector.x * 30) + "px";
    rightFeedback.style.top = ( data.clientY + data.vector.y * 30) + "px";
});

rightJoystick.on('end', function() {
    socket.emit("joystick_destroy", { side: "right" })
    rightFeedback.style.display = 'none';
});

document.getElementById('joystick-zone-left').addEventListener('touchend', function(event) {
    socket.emit("joystick_destroy", { side: "left", joystick: !!leftJoystick });
});

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