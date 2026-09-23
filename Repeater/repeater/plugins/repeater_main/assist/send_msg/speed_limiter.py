import time
import asyncio
from typing import Awaitable, TypeVar
from nonebot import logger

T = TypeVar("T")

class SpeedLimiter:
    def __init__(
            self,
            limit_speed_per_minute: int | float | None = 100
        ):
        self.limit_speed_per_minute = limit_speed_per_minute
        self.last_submit_time = time.monotonic_ns()
        self.lock = asyncio.Lock()
    
    async def submit(self, task: Awaitable[T]) -> T:
        async with self.lock:
            if self.limit_speed_per_minute is not None:
                current_time = time.monotonic_ns()
                last_time_dalta = current_time - self.last_submit_time
                expected_time_delta = 60 / self.limit_speed_per_minute
                time_dalta = max(0, expected_time_delta - (last_time_dalta / 1e9))
                if time_dalta > 0:
                    logger.info(
                        "Limit speed: {speed_limit}/min, sleep {time_dalta:.2f} sec",
                        speed_limit = self.limit_speed_per_minute,
                        time_dalta = time_dalta
                    )
                    await asyncio.sleep(time_dalta)
            result = await task
            self.last_submit_time = time.monotonic_ns()
            return result