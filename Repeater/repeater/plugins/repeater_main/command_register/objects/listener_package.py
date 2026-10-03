import uuid
import asyncio

from contextvars import Context
from typing import (
    Any,
    Awaitable,
    Callable,
    Generator,
)
from types import (
    GenericAlias
)

from dataclasses import dataclass
from ...assist import PersonaInfo, Namespace

@dataclass
class ListenerPackage(Awaitable[PersonaInfo]):
    """
    ListenerPackage
    """
    future: asyncio.Future[PersonaInfo]
    """Waiting for a PersonaInfo."""
    target: Namespace
    """Target namespace."""
    id: uuid.UUID
    """Package listener_id."""
    sponsor: uuid.UUID
    """Sponsor task_id."""
    block_propagation: bool = False
    """To prevent information from being spread down. (Exclusive mode)"""

    def get_loop(self) -> asyncio.AbstractEventLoop:
        """Get the loop."""
        return self.future.get_loop()
    
    def add_done_callback(self, fn: Callable[[asyncio.Future[PersonaInfo]], object], /, *, context: Context | None = None) -> None:
        """
        Add a callback to be run when the future is done.

        The callback is called with a single argument - the future object. If the future is already done when this is called, the callback is scheduled with call_soon.
        """
        self.future.add_done_callback(fn, context = context)
    
    def cancel(self, msg: Any | None = None) -> bool:
        """
        Cancel the future if not done.

        If the future is already done or cancelled, return False. Otherwise, change the future's state to cancelled, schedule the callbacks and return True.
        """
        return self.future.cancel(msg)

    def cancelled(self) -> bool:
        """Return True if the future has been cancelled."""
        return self.future.cancelled()
    
    def done(self) -> bool:
        """
        Return True if the future has been completed.

        Done means either that a result / exception are available, or that the future was cancelled.
        """
        return self.future.done()

    def result(self) -> PersonaInfo:
        """
        Return the result of the future.

        If the future has been cancelled, raises CancelledError. If the future's result isn't yet available, raises InvalidStateError. If the future is done and has an exception set, this exception is raised.
        """
        return self.future.result()
    
    def exception(self) -> BaseException | None:
        """
        Return the exception that was set on this future.

        The exception (or None if no exception was set) is returned only if the future is done. If the future has been cancelled, raises CancelledError. If the future isn't done yet, raises InvalidStateError.
        """
        return self.future.exception()
    
    def remove_done_callback(self, fn: Callable[[asyncio.Future[PersonaInfo]], object], /) -> int:
        """
        Remove all instances of a callback from the "call when done" list.

        Returns the number of callbacks removed.
        """
        return self.future.remove_done_callback(fn)

    def set_result(self, result: PersonaInfo, set_sponsor: bool = True) -> None:
        """
        Mark the future done and set its result.

        If the future is already done when this method is called, raises InvalidStateError.
        """
        if set_sponsor:
            result.copy(task_id = self.sponsor)
            self.future.set_result(result)
        else:
            self.future.set_result(result)
    
    def set_exception(self, exception: type | BaseException, /) -> None:
        """
        Mark the future done and set an exception.

        If the future is already done when this method is called, raises InvalidStateError.
        """
        self.future.set_exception(exception)

    def __iter__(self) -> Generator[Any, None, PersonaInfo]:
        """
        Implement iter(self).
        """
        return self.future.__iter__()

    def __await__(self) -> Generator[Any, None, PersonaInfo]:
        """
        Return an iterator to be used in await expression.
        """
        return self.future.__await__()

    def __class_getitem__(cls, item: type[PersonaInfo]) -> GenericAlias:
        """
        See PEP 585
        """
        return cls.future.__class_getitem__(item)