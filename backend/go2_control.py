# Manages the connection to the go2 robot

import asyncio
from dataclasses import dataclass
import logging
import json
import pprint
import time
from typing import Any, Coroutine, Dict

from go2_webrtc_driver.webrtc_driver import (
    Go2WebRTCConnection,
    WebRTCConnectionMethod
)
from go2_webrtc_driver.constants import DATA_CHANNEL_TYPE, RTC_TOPIC, SPORT_CMD

from go2_control_interface import Go2ControlInterface, Gait

# Create a console logger:
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().addHandler(logging.StreamHandler())

@dataclass
class VelocityCmd:
    vx: float = 0
    vy: float = 0
    vyaw: float = 0


class Go2Control(Go2ControlInterface):
    def __init__(self, connection_method: WebRTCConnectionMethod, ip: str):
        self.ip = ip
        self.connection_method = connection_method
        self.connection: None | Go2WebRTCConnection = None
        self._velocity_cmd = VelocityCmd()

    @property
    def is_connected(self):
        if not self.connection:
            return False

        return self.connection.isConnected

    async def connect(self) -> Dict[str, Any]:
        try:
            self.connection = Go2WebRTCConnection(self.connection_method, ip=self.ip)
            logging.warning(f"Attempting to connect to robot at ip={self.ip}...")
            await self.connection.connect()
            logging.warning(f"Connection attempt complete {self.connection.isConnected=}")
            if self.connection.isConnected:
                return {"connected": True}
            else:
                return {"error": "Failed to connect to robot"}
        except Exception as e:
            return {"error": str(e)}

    async def _publish_request(self, topic: str, options: Any | None = None) -> Coroutine[Any, Any, Any | None]:
        return await self.connection.datachannel.pub_sub.publish_request_new(
            topic,
            options
        )

    async def get_mode(self) -> str | None:
        response = await self._publish_request(
            RTC_TOPIC["MOTION_SWITCHER"],
            {"api_id": 1001},
        )

        if response['data']['header']['status']['code'] == 0:
            data = json.loads(response['data']['data'])
            return data['name']

    async def switch_to_normal_mode(self):
        current_mode = await self.get_mode()

        if not current_mode or current_mode != "normal":
            tic = time.time_ns()
            logging.warning(f"Switching motion mode from {current_mode} to 'normal' mode")
            resp = await self._publish_request(
                RTC_TOPIC["MOTION_SWITCHER"],
                {
                    "api_id": 1002,
                    "parameter": {"name": "normal"},
                }
            )
            # TODO: Maybe there's a topic we can subscribe to in order to know what state
            #       the robot is in so we don't need to sleep arbitrarily long
            logging.warning(f"Response took {time.time_ns() - tic}ns")
            await asyncio.sleep(2)

    async def switch_to_ai_mode(self):
        current_mode = await self.get_mode()

        if not current_mode or current_mode != "ai":
            tic = time.time_ns()
            logging.warning(f"Switching motion mode from {current_mode} to 'ai' mode")
            resp = await self._publish_request(
                RTC_TOPIC["MOTION_SWITCHER"],
                {
                    "api_id": 1002,
                    "parameter": {"name": "ai"}
                }
            )
            # TODO: Maybe there's a topic we can subscribe to in order to know what state
            #       the robot is in so we don't need to sleep arbitrarily long
            logging.warning(f"Response took {time.time_ns() - tic}ns")
            await asyncio.sleep(2)


    async def sport_mode_request(self, mode: str):
        return await self._publish_request(
            RTC_TOPIC["SPORT_MOD"],
            {"api_id": SPORT_CMD[mode]}
        )

    async def set_gait(self, gait: Gait):
        await self._publish_request(RTC_TOPIC["SPORT_MOD"],
                                    {
                                        "api_id": SPORT_CMD["SwitchGait"],
                                        "data": gait.value,
                                    })

    async def stand(self):
        await self.sport_mode_request("RecoveryStand")
        await asyncio.sleep(2)
        return await self.sport_mode_request("BalanceStand")

    async def sit(self):
        return await self.sport_mode_request("StandDown")

    async def walk_enable(self):
        logging.error("Sending key to enable walking!")
        await self.connection.datachannel.pub_sub.publish(
            RTC_TOPIC["WIRELESS_CONTROLLER"],
            {
                "api_id": 0,
                "parameter": {"lx": 0, "ly": 0, "rx": 0, "ry": 0, "keys": 4}
            }
        )

    async def move(self, vx: float | None = None, vy: float | None = None, vyaw: float | None = None):
        if not vx and not vy and not vyaw:
            return
        if vx:
            self._velocity_cmd.vx = vx
        else:
            # Decay the command so it isn't stuck
            self._velocity_cmd.vx *= 0.95
        if vy:
            self._velocity_cmd.vy = vy
        else:
            # Decay the command so it isn't stuck
            self._velocity_cmd.vy *= 0.95
        if vyaw:
            self._velocity_cmd.vyaw = vyaw
        else:
            # Decay the command so it isn't stuck
            self._velocity_cmd.vyaw *= 0.95

        logging.warning(f"Sending command: {self._velocity_cmd}")

        resp = await self._publish_request(
            RTC_TOPIC["SPORT_MOD"],
            {
                "api_id": SPORT_CMD["Move"],
                "parameter": {
                    "x": self._velocity_cmd.vx,
                    "y": self._velocity_cmd.vy,
                    "z": self._velocity_cmd.vyaw,
                },
                "id": 918514952
            }
        )
        print("move command response:")
        pprint.pprint(resp)
