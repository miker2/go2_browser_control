var socket = io();

function isTouchDevice() {
    return (('ontouchstart' in window) ||
       (navigator.maxTouchPoints > 0) ||
       (navigator.msMaxTouchPoints > 0));
}

document.getElementById('connect-button').addEventListener('click', function(event) {
    console.log('Ready to connect');
    socket.emit("connect_webrtc", { data: 'connect' });

    document.getElementById('status-msg').innerText = 'Connecting...';
    element = document.getElementById('connecting');
    element.classList.add("lds-ripple");

    // TODO: add some indication of the connection status to the user
    
});

socket.on('connection_response', function(data) {
    // Update page data here as connection is established
    console.log('Received data:', data);

    if (data.connected) {
        document.getElementById('status-msg').innerText = 'Connected!';
        // sleep for 2 seconds
        setTimeout(function() {
            window.location.href = '/control';
        }
        , 2000);
    } else {
        // Notify the user that the connected failed via a popup alert
        alert('Connection failed. Please try again.');
        // Reset the connection status:
        document.getElementById('status-msg').innerText = 'Connection failed. Please try again.';
        document.getElementById('connecting').classList.remove("lds-ripple");
    }
});