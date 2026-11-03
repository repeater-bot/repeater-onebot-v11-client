from typing import (
    TypeVar,
    Generic,
    Hashable
)
from .callback import (
    ETCCallbackType
)

KEY = TypeVar("KEY", bound = Hashable)
CALLBACK_TYPE = TypeVar("CALLBACK_TYPE")

class Register(Generic[KEY, CALLBACK_TYPE]):
    def __init__(self):
        self._commands: dict[KEY, CALLBACK_TYPE] = {}

    def __len__(self) -> int:
        return len(self._commands)

    def __iter__(self):
        return iter(self._commands.values())

    def __contains__(self, id: KEY) -> bool:
        return id in self._commands

    def __getitem__(self, id: KEY) -> CALLBACK_TYPE:
        return self._commands[id]

    def __setitem__(self, id: KEY, command: CALLBACK_TYPE) -> None:
        self.register(id, command)

    def __delitem__(self, id: KEY) -> None:
        del self._commands[id]

    def keys(self) -> list[KEY]:
        return list(self._commands.keys())

    def values(self) -> list[CALLBACK_TYPE]:
        return list(self._commands.values())

    def items(self) -> list[tuple[KEY, CALLBACK_TYPE]]:
        return list(self._commands.items())
    
    def register(self, id: KEY, command: CALLBACK_TYPE) -> None:
        """Register a command to the register."""
        self._commands[id] = command

    def unregister(self, id: KEY) -> None:
        """Unregister a command from the register."""
        if id in self._commands:
            self._commands.pop(id)

    def get(self, id: KEY) -> CALLBACK_TYPE | None:
        """Get a command from the register."""
        return self._commands.get(id)

register_external_trigger: Register[str, ETCCallbackType] = Register()