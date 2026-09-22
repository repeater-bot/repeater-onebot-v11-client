from typing import Callable, Awaitable
from nonebot.adapters.onebot.v11 import MessageEvent, Message

CALLABLE_TYPE = Callable[
    [
        str,
        MessageEvent,
        Message
    ],
    Awaitable[
        tuple[list[Message], int]
    ]
]

class Register:
    def __init__(self):
        self._commands: dict[str, CALLABLE_TYPE] = {}

    def __len__(self) -> int:
        return len(self._commands)

    def __iter__(self):
        return iter(self._commands.values())

    def __contains__(self, id: str) -> bool:
        return id in self._commands

    def __getitem__(self, id: str) -> CALLABLE_TYPE:
        return self._commands[id]

    def __setitem__(self, id: str, command: CALLABLE_TYPE) -> None:
        self.register(id, command)

    def __delitem__(self, id: str) -> None:
        del self._commands[id]

    def keys(self) -> list[str]:
        return list(self._commands.keys())

    def values(self) -> list[CALLABLE_TYPE]:
        return list(self._commands.values())

    def items(self) -> list[tuple[str, CALLABLE_TYPE]]:
        return list(self._commands.items())
    
    def register(self, id: str, command: CALLABLE_TYPE) -> None:
        """Register a command to the register."""
        self._commands[id] = command

    def unregister(self, id: str) -> None:
        """Unregister a command from the register."""
        if id in self._commands:
            self._commands.pop(id)

    def get(self, id: str) -> CALLABLE_TYPE | None:
        """Get a command from the register."""
        return self._commands.get(id)

register_external_trigger = Register()