var socket = io();

function isTouchDevice() {
    return (('ontouchstart' in window) ||
       (navigator.maxTouchPoints > 0) ||
       (navigator.msMaxTouchPoints > 0));
}

document.getElementById('connect-button').addEventListener('click', function() {
    console.log('Ready to connect');
    socket.emit('connect-to-robot', { });

    // TODO: add some indication of the connection status to the user
    
});

socket.on('render_response', function(data) {
    // Update page data here as connection is established
    console.log('Received data:', data);

    window.location.href = '/control';
});