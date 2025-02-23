from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio

import os

from go2_webrtc_driver.webrtc_driver import (
    # Go2WebRTCConnection, 
    WebRTCConnectionMethod
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '../frontend'))

### PLACEHOLDER FOR THE Go2WebRTCConnection CLASS
class Go2WebRTCConnection:
    def __init__(self, *args, **kwargs):
        #... your initialization logic...
        pass

    async def connect(self):
        #... your async connect logic...
        # Simulate a connection attempt (replace with your actual logic)
        await asyncio.sleep(5)  # Simulate connection time
        return True  # Or False if connection fails


app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/control")
async def root(request: Request):
    return templates.TemplateResponse("control.html", {"request": request})

async def connect_to_robot():
    try:
        connection = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip="192.168.123.161")
        print('Attempting to conect to robot...')
        result = await connection.connect()
        print(f"Connection attempt complete {result=} .....")
        if result:
            return {"connected": True}
        else:
            return {"error": "Failed to connect to robot"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/connect")
async def async_connect_to_robot():
    try:
        # Wait for the connect_to_robot task to complete with a timeout:
        result = await asyncio.wait_for(connect_to_robot(), timeout=15)
        print(f"Connection result: {result=}")
        return result  # Return the result of the connection attemp
    except asyncio.TimeoutError:
        print("Connection attempt timed out")
        return {"error": "Connection attempt timed out"}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}



# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         await websocket.send_text(f"Message text was: {data}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
