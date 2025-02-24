function isTouchDevice() {
    return (('ontouchstart' in window) ||
       (navigator.maxTouchPoints > 0) ||
       (navigator.msMaxTouchPoints > 0));
}

let leftFeedback = document.getElementById('joystick-feedback-left');
let rightFeedback = document.getElementById('joystick-feedback-right');
console.log("Websocket will be opened at: " + window.location.host);
var ws = new WebSocket('ws://' + window.location.host + '/joystick');

function createJoystick(side, color, signal, feedback) {
    var joystick = nipplejs.create({
        zone: document.getElementById('joystick-zone-' + side),
        color: color,
        mode: 'dynamic'
    });

    function sendData(x, y) {
        ws.send(JSON.stringify({side: side,
                                signal: signal,
                                x: x,
                                y: y
        }));
    }

    joystick.on('move', function(evt, data) {
        console.log(side + " Joystick Move", data);
        sendData(data.vector.x, data.vector.y);

        feedback.style.display = 'block';
        feedback.style.left = ( data.position.x + data.vector.x * 30) + "px";
        feedback.style.top = ( data.position.y - data.vector.y * 30) + "px";
    });

    joystick.on('end', function() {
        console.log(side + " Joystick End");
        feedback.style.display = 'none';
        sendData(0.0, 0.0)
    });
}

var leftJoystick = createJoystick('left', 'blue', 'move', leftFeedback);
var rightJoystick = createJoystick('right', 'red', 'rotate', rightFeedback);


document.getElementById('joystick-zone-left').addEventListener('touchend', () => {});

document.getElementById('joystick-zone-right').addEventListener('touchend', () => {});


async function awaitCommandResponse(cmd_data) {
    console.log('Sending command:', cmd_data);

    try {
        const response = await fetch('/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(cmd_data)
        })

        const data = await response.json();
        console.log('Data:', data);
    } catch (error) {
        console.error('Caught Error:', error)
    }
}

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
        awaitCommandResponse({ type: "voice", command: command });
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

function setupButton(buttonId, command, hold) {
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
            console.log(command, 'pressed');
            // socket.emit(eventName, { pressed: true });
        }
    });

    button.addEventListener(touch_end, function() {
        this.classList.remove("active");
        if (hold) {
            console.log(command, 'released');
            // socket.emit(eventName, { pressed: false });
        }
    });

    if (!hold) {
        button.addEventListener('click', function() {
            console.log(command, 'clicked');
            awaitCommandResponse({ type: "action", command: command });
        });
    }
}

setupButton('action-button', 'Dance2', false);
setupButton('sit-button', 'StandDown', false);
setupButton('stand-button', 'RecoveryStand', false);

document.getElementById('execute-button').addEventListener('click', function() {
    let command = document.getElementById('action-select').value;
    console.log('Command:', command);
    awaitCommandResponse({ type: "action", command: command });
});