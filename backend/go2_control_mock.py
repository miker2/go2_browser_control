import asyncio
from typing import Any, Dict

from go2_control_interface import Go2ControlInterface, Gait

### PLACEHOLDER FOR THE Go2WebRTCConnection CLASS
class Go2ControlMock(Go2ControlInterface):
    def __init__(self, *args, **kwargs):
        #... your initialization logic...
        self._is_connected = False
        self._current_mode = "normal"

    @property
    def is_connected(self):
        return self._is_connected

    async def connect(self) -> Dict[str, Any]:
        #... your async connect logic...
        self._is_connected = False
        # Simulate a connection attempt (replace with your actual logic)
        await asyncio.sleep(5)  # Simulate connection time
        self._is_connected = True
        return {"connected": True}

    async def get_mode(self) -> str | None:
        await asyncio.sleep(1)
        return self._current_mode

    async def switch_to_normal_mode(self):
        await asyncio.sleep(1)
        self._current_mode = "normal"

    async def switch_to_ai_mode(self):
        await asyncio.sleep(1)
        self._current_mode = "ai"

    async def sport_mode_request(self, mode):
        await asyncio.sleep(1)

    async def set_gait(self, gait: Gait):
        await asyncio.sleep(1)

    async def stand(self):
        await asyncio.sleep(1)

    async def sit(self):
        await asyncio.sleep(1)

    def move(self, vx: float | None = None, vy: float | None = None, vyaw: float | None = None):
        pass
