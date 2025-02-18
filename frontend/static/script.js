var socket = io();

function isTouchDevice() {
    return (('ontouchstart' in window) ||
       (navigator.maxTouchPoints > 0) ||
       (navigator.msMaxTouchPoints > 0));
}

let leftFeedback = document.getElementById('joystick-feedback-left');
let rightFeedback = document.getElementById('joystick-feedback-right');

function createJoystick(side, color, signal, feedback) {
    var joystick = nipplejs.create({
        zone: document.getElementById('joystick-zone-' + side),
        color: color,
        mode: 'dynamic'
    });

    joystick.on('move', function(evt, data) {
        console.log(side + " Joystick Move", data);
        socket.emit(signal, { x: data.vector.x, y: data.vector.y });

        feedback.style.display = 'block';
        feedback.style.left = ( data.position.x + data.vector.x * 30) + "px";
        feedback.style.top = ( data.position.y - data.vector.y * 30) + "px";
    });

    joystick.on('end', function() {
        console.log(side + " Joystick End");
        socket.emit("joystick_destroy", { side: side });
        feedback.style.display = 'none';
    });
}

var leftJoystick = createJoystick('left', 'blue', 'move', leftFeedback);
var rightJoystick = createJoystick('right', 'red', 'rotate', rightFeedback);


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

function setupButton(buttonId, eventName, hold) {
    var touch_start = 'mousedown';
    var touch_end = 'mouseup';
    if (isTouchDevice()) {
        touch_start = 'touchstart';
        touch_end = 'touchend';
    }
    let button = document.getElementById(buttonId);
    button.addEventListener(touch_start, function() {
        this.classList.add("active");
        if (hold) {
            console.log(eventName, 'pressed');
            socket.emit(eventName, { pressed: true });
        }
    });

    button.addEventListener(touch_end, function() {
        this.classList.remove("active");
        if (hold) {
            console.log(eventName, 'released');
            socket.emit(eventName, { pressed: false });
        }
    });

    if (!hold) {
        button.addEventListener('click', function() {
            console.log(eventName, 'clicked');
            socket.emit(eventName, { pressed: true });
        });    
    }
}

setupButton('action-button', 'action', true);
setupButton('sit-button', 'sit', false);
setupButton('stand-button', 'stand', false);

document.getElementById('execute-button').addEventListener('click', function() {
    let command = document.getElementById('action-select').value;
    console.log('Command:', command);
    socket.emit('command', { command: command });
});