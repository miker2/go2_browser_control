// This script is used to connect to the robot and redirect to the control page
// when the user clicks the "Connect" button.

function isTouchDevice() {
    return (('ontouchstart' in window) ||
       (navigator.maxTouchPoints > 0) ||
       (navigator.msMaxTouchPoints > 0));
}

async function awaitConnectionResponse() {
    console.log('Ready to connect');
    document.getElementById('status-msg').innerText = 'Connecting...';
    element = document.getElementById('connecting');
    element.classList.add("lds-ripple");

    try {
        const response = await fetch('/connect', { method: 'POST' });
        console.log('Response:', response);

        const data = await response.json();
        console.log('Data:', data);

        if (data.connected) {
            console.log("Connected to robot!");
            document.getElementById('status-msg').innerText = 'Connected!';
            // sleep for 5 seconds
            setTimeout(function() {
                window.location.href = '/control';
            }
            , 5000);
        } else {
            console.error("Error: ", data.error);
            // Notify the user that the connection failed via a popup alert
            alert('Connection failed. Please try again.');
            // Reset the connection status:
            document.getElementById('status-msg').innerText = 'Connection failed. Please try again.';
            document.getElementById('connecting').classList.remove("lds-ripple");
        }
    } catch (error) {
        console.error('Error:', error)
        // Handle fetch error
    }
}

document.getElementById('connect-button').addEventListener('click', awaitConnectionResponse);
