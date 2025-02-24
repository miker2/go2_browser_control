from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import asyncio
import json
import os
import pprint

from thefuzz import fuzz, process

USE_MOCK = False
# This is the wired address
ROBOT_IP_ADDR = "192.168.123.161"
# Wireless IP address (used for testing)
ROBOT_IP_ADDR = "10.0.0.8"


if USE_MOCK:
    from go2_control_mock import Go2ControlMock as Go2Control
else:
    from go2_control import Go2Control

from go2_webrtc_driver.webrtc_driver import WebRTCConnectionMethod
from go2_webrtc_driver.constants import SPORT_CMD

import utils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '../frontend'))


app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))

go2_control = Go2Control(WebRTCConnectionMethod.LocalSTA, ROBOT_IP_ADDR)

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/control")
async def root(request: Request):
    return templates.TemplateResponse("control.html", {"request": request})

@app.post("/connect")
async def async_connect_to_robot():
    try:
        # Wait for the connect_to_robot task to complete with a timeout:
        result = await asyncio.wait_for(go2_control.connect(), timeout=30)
        print(f"Connection result: {result=}")
        return result  # Return the result of the connection attemp
    except asyncio.TimeoutError:
        print("Connection attempt timed out")
        return {"error": "Connection attempt timed out"}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

async def handle_action(command: str):
    print(f"Action data: {command}")
    # ... robot control logic ...
    response = await go2_control.sport_mode_request(command)

    pprint.pprint(response)

    return {"status": "OK"}

async def handle_voice(voice_str: str):
    print(f"Voice data: {voice_str}")
    res = process.extractOne(
        utils.snake_to_upper_camel(voice_str.replace(" ", "_")),
        SPORT_CMD.keys(),
        scorer=fuzz.partial_token_sort_ratio,
    )
    print(f"Matched command: {res}")
    cmd, match_ratio = res
    if match_ratio < 75:
        return {"error": f"Command not recognized. Received: {voice_str}, Result {res}"}
    # ... voice control logic ...
    return handle_action(res[0])

@app.post("/command")
async def command(data: dict):
    print(f"Action data: {data}")
    print("type: ", data.get("type"))
    match data.get("type"):
        case "action":
            return await handle_action(data.get("command"))
        case "voice":
            return await handle_voice(data.get("command"))
        case _:
            return {"error": f"Invalid command type: ({data.get('type')})"}

@app.websocket("/joystick")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Websocket connection established")
    try:
        while True:
            data = await websocket.receive_text()
            # Convert the received data to a dictionary
            data = json.loads(data)
            print(f"Joystick data: {data}")
            match data.get("signal"):
                case "start":
                    await go2_control.walk_enable()
                case "move":
                    # forward, backward, left, right
                    # Scale the lateral velocity command to be a bit safer
                    await go2_control.move(vx=data['y'], vy=-0.25 * data['x'])
                case "rotate":
                    # yaw and pitch
                    # Scale the yaw-rate command down a bit
                    await go2_control.move(vyaw=-0.5 * data['x'])
                case _:
                    print("Unknown signal type!")

            # Perhaps here we can subscribe to the sport mode state topic and
            # display some useful information to the user
            # await websocket.send_text(f"WS: {data}")
    except WebSocketDisconnect:
        print("Websocket disconnected")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
