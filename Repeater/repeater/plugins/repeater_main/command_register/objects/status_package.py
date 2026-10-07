import uuid
import asyncio
from dataclasses import dataclass

@dataclass
class StatusPackage:
    """
    This class is used to store the status of the repeater.
    """

    event: asyncio.Event
    """Status finish event."""

    status_id: uuid.UUID
    """Status id."""

    sponsor: uuid.UUID
    """Task id of the task that created the state."""

    def is_finished(self) -> bool:
        """
        Check whether the status has been turned off.
        """
        return self.event.is_set()

    def finish(self) -> None:
        """
        Turn off the status.
        """
        self.event.set()

    async def wait_finish(self) -> None:
        """
        Wait until the status is turned off.
        """
        await self.event.wait()

    def clear(self) -> None:
        """
        Clear the status.
        """
        self.event.clear()