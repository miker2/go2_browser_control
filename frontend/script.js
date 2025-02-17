const joystickArea = document.getElementById('joystick-area');
let socket = io('ws://' + window.location.hostname + ':5000'); // Dynamic server address

function createJoystick(joystickId) {
    const joystick = document.getElementById(joystickId);
    const nipple = new Nipple({
        zone: joystick,
        mode: 'static',
        position: { left: '50%', top: '50%' },
        size: 100,
        color: 'gray'
    });

    nipple.on('move', (evt, data) => {
        if (data && data.vector) {
            const x = data.vector.x;
            const y = data.vector.y;
            socket.emit('joystick', { joystick: joystickId, x, y });
        }
    });

    nipple.on('end', () => {
      socket.emit('joystick', { joystick: joystickId, x: 0, y: 0 }); // Reset on release
    })

    return nipple;
}

joystickArea.addEventListener('touchstart', (event) => {
    if (event.target === joystickArea) {
        const touch = event.touches[0];
        const joystick1Rect = document.getElementById('joystick1').getBoundingClientRect();
        const joystick2Rect = document.getElementById('joystick2').getBoundingClientRect();

        if (!joystick1Rect.width) {
            document.getElementById('joystick1').style.left = (touch.clientX - 50) + 'px';
            document.getElementById('joystick1').style.top = (touch.clientY - 50) + 'px';
            createJoystick('joystick1');
        } else if (!joystick2Rect.width) {
            document.getElementById('joystick2').style.left = (touch.clientX - 50) + 'px';
            document.getElementById('joystick2').style.top = (touch.clientY - 50) + 'px';
            createJoystick('joystick2');
        }
    }
}, {once: true});


// Speech Recognition
const speechButton = document.getElementById('speech-button');
let listening = false;

const recognition = new webkitSpeechRecognition() || new SpeechRecognition();
recognition.continuous = false;
recognition.interimResults = false;

recognition.onstart = () => {
    listening = true;
    speechButton.textContent = "Stop Listening";
};

recognition.onend = () => {
    listening = false;
    speechButton.textContent = "Start Listening";
};

recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    listening = false;
    speechButton.textContent = "Start Listening";
};

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript.toLowerCase();
    console.log("Speech recognized:", transcript);

    let command = null;
    if (transcript.includes("forward")) {
        command = "forward";
    } else if (transcript.includes("backward")) {
        command = "backward";
    } else if (transcript.includes("left")) {
        command = "left";
    } else if (transcript.includes("right")) {
        command = "right";
    } else if (transcript.includes("stop")) {
        command = "stop";
    } else if (transcript.includes("sit")) {
        command = "sit";
    } else if (transcript.includes("stand")) {
        command = "stand";
    } else if (transcript.includes("dance")) {
        command = "dance";
    } else if (transcript.includes("pounce")) {
        command = "pounce";
    } else if (transcript.includes("jump")) {
        command = "jump";
    }

    if (command) {
        socket.emit('command', command);
    } else {
      console.log("No matching command found")
    }
};

speechButton.addEventListener('click', () => {
    if (!listening) {
        recognition.start();
    } else {
        recognition.stop();
    }
});
