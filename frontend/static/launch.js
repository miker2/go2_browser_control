// This script is used to connect to the robot and redirect to the control page
// when the user clicks the "Connect" button.

function isTouchDevice() {
    return (('ontouchstart' in window) ||
       (navigator.maxTouchPoints > 0) ||
       (navigator.msMaxTouchPoints > 0));
}

status_msg = document.getElementById('status-msg')
busy_wait = document.getElementById('connecting')

async function awaitConnectionResponse() {
    console.log('Ready to connect');
    status_msg.innerText = 'Connecting...';
    busy_wait.classList.add("lds-ripple");

    try {
        const response = await fetch('/connect', { method: 'POST' });
        console.log('Response:', response);

        const data = await response.json();
        console.log('Data:', data);

        if (data.connected) {
            console.log("Connected to robot!");
            status_msg.innerText = 'Connected!';
            // sleep for 2 seconds
            setTimeout(function() {
                window.location.href = '/control';
            }
            , 2000);
        } else {
            // Reset the connection status:
            status_msg.innerText = 'Not Connected';
            busy_wait.classList.remove("lds-ripple");

            setTimeout(() => {
                // Notify the user that the connection failed via a popup alert
                alert('Connection failed! Ensure robot is on and try again.');
            }, 100);

            console.error("Error: ", data.error);
        }
    } catch (error) {
        console.error('Caught Error:', error)

        // Reset the connection status:
        status_msg.innerText = 'Not Connected';
        busy_wait.classList.remove("lds-ripple");

        // Handle fetch error
    }
}

document.getElementById('connect-button').addEventListener('click', awaitConnectionResponse);
