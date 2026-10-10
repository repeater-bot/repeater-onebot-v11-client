import uuid
import asyncio
from dataclasses import dataclass

@dataclass
class StatusPackage:
    """
    This class is used to store the status of the repeater.
    """

    future: asyncio.Future[None]
    """Status finish event."""

    status_id: uuid.UUID
    """Status id."""

    sponsor: uuid.UUID
    """Task id of the task that created the state."""

    def is_finished(self) -> bool:
        """
        Check whether the status has been turned off.
        """
        return self.future.done()

    def finish(self) -> None:
        """
        Turn off the status.
        """
        self.future.set_result(None)

    async def wait_finish(self) -> None:
        """
        Wait until the status is turned off.
        """
        await self.future

    def reset(self) -> None:
        """
        Clear the status.
        """
        loop = asyncio.get_running_loop()
        self.future = loop.create_future()

    def cancel(self) -> None:
        """
        Cancel the status.
        """
        self.future.cancel()