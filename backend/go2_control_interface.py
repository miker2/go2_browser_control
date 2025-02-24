from abc import ABC, abstractmethod

from typing import Any, Dict

from enum import Enum

# Create an enum for the different gaits:
class Gait(Enum):
    IDLE = 0
    TROT = 1
    JOG = 2
    STAIRS = 3
    OBSTACLE_AVOID = 4

class Go2ControlInterface(ABC):

    @property
    @abstractmethod
    def is_connected(self):
        pass

    @abstractmethod
    async def connect(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_mode(self) -> str | None:
        pass

    @abstractmethod
    async def switch_to_normal_mode(self):
        pass

    @abstractmethod
    async def switch_to_ai_mode(self):
        pass

    @abstractmethod
    async def sport_mode_request(self, mode: str):
        pass

    @abstractmethod
    async def set_gait(self, gait: Gait):
        pass

    @abstractmethod
    async def stand(self):
        pass

    @abstractmethod
    async def sit(self):
        pass

    @abstractmethod
    def move(self, vx: float | None = None, vy: float | None = None, vyaw: float | None = None):
        pass
