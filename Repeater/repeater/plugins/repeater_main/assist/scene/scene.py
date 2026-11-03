import re
import hashlib
import base64
from pydantic import BaseModel, ConfigDict
from ...client_configs import storage_configs
from .message_source import MessageSource

pattern = re.compile(r"^Scene_(?P<mode>group|private)_(?P<id>[0-9]+)?$")
no_id_pattern = re.compile(r"^Scene_(?P<mode>group|private)$")

class Scene(BaseModel):
    """
    对话场景
    """
    model_config = ConfigDict(
        frozen = True
    )

    source: MessageSource = MessageSource.GROUP
    id: str | None = None

    @property
    def is_group(self) -> bool:
        return self.source == MessageSource.GROUP

    @property
    def is_private(self) -> bool:
        return self.source == MessageSource.PRIVATE

    @classmethod
    def from_str(cls, string: str) -> "Scene":
        if storage_configs.hash_scene_iterations > 0:
            raise RuntimeError("Hashed namespace can not be deserialized!")
        match_result = pattern.match(string)
        if match_result is not None:
            return cls(
                source = MessageSource(value=match_result.group("mode")),
                id = match_result.group("id")
            )

        match_result = no_id_pattern.match(string)
        if match_result is not None:
            return cls(
                source = MessageSource(value=match_result.group("mode")),
                id = None
            )

        raise ValueError(f"Invalid namespace string: {string}")

    @property
    def _scene(self) -> str:
        if self.id is None:
            return f"Scene_{self.source.value}"
        else:
            return f"Scene_{self.source.value}_{self.id}"

    @staticmethod
    def _hash_str(string: str) -> str:
        if storage_configs.hash_scene_iterations > 0:
            return base64.urlsafe_b64encode(
                hashlib.pbkdf2_hmac(
                    hash_name = "sha3_256",
                    password = string.encode("utf-8"),
                    salt = storage_configs.hash_scene_salt.encode("utf-8"),
                    iterations = storage_configs.hash_scene_iterations
                )
            ).decode("utf-8")
        else:
            return string

    @property
    def scene_str(self):
        return self._hash_str(self._scene)
    
    def __str__(self) -> str:
        return self.scene_str