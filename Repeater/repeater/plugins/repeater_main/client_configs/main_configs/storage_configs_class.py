import secrets
from pydantic import BaseModel, Field

from .camouflage import Camouflage
from .text_length_score_configs import TextLengthScoreConfigs
from .server_api_timeout import ServerAPITimeout
from ..useless_button_words_list import useless_button_words
from .behavioral_act import BehavioralACT
from .hello_content import HelloContent
from .platform_interface import PlatformInterface
from .loading import LoadingConfigs
from .generate_image_file_type import GenerateImageFileType
from .render_error_message import RenderErrorMessage
from .cilent_limits import ClientLimits
from .ignore_enter import IgnoreEnter
from .permission_rule import PermissionRule

class StorageConfigs(BaseModel):
    text_length_score_configs: TextLengthScoreConfigs = Field(default_factory = TextLengthScoreConfigs)
    hello_content: HelloContent = Field(default_factory = HelloContent)
    loading: LoadingConfigs = Field(default_factory = LoadingConfigs)
    behavioral_acts: dict[str, BehavioralACT] = Field(default_factory=dict)
    default_behavioral_act: BehavioralACT = Field(default_factory=BehavioralACT)
    backends: dict[str, str] = Field(default_factory=dict)
    default_backend: str = ""
    handler_timeout: int | float | None = Field(default=None, gt=0)
    client_pool_size: int = Field(default=10, ge=1)
    usage_group_context: bool = False
    server_api_timeout: ServerAPITimeout = Field(default_factory = ServerAPITimeout)
    camouflage: Camouflage = Field(default_factory = Camouflage)
    generate_image_file_type: GenerateImageFileType = GenerateImageFileType.URL
    render_error_message: RenderErrorMessage = Field(default_factory = RenderErrorMessage)
    client_limits: ClientLimits = Field(default_factory = ClientLimits)
    ignore_enter: IgnoreEnter = Field(default_factory = IgnoreEnter)
    super_permissions: list[PermissionRule] = Field(default_factory = list)
    summarize_and_contract_default_message: str = "System Message: please sum up all the contents above."
    ciallo_content: str = "Ciallo~ (∠・ω< )⌒★"
    branch_file_size_use_abbreviation: bool = True
    hash_namespace_salt: str = Field(default_factory = lambda: secrets.token_urlsafe(64))
    hash_namespace_iterations: int = 0
    max_tool_response_length: int | None = 100
    allow_send_any_message: bool = False
    model_first_chunk_timeout: int | float | None = 90.0
    tokenizer_cache_size: int = 50
    tokenizer_most_frequent_tokens: int = 5
    max_reply_chain_length: int | None = 5
    max_text_file_size: int | None = None
    text_file_encoding: str = "utf-8"
    log_registed_handler_name: bool = True
    platform_interface: PlatformInterface = Field(default_factory=PlatformInterface)
    useless_button_words: list[str] = Field(default_factory=lambda: useless_button_words)
    useless_button_missing: str = "The button buzzed away."
    
    def get_behavioral_act(self, user_id: str) -> BehavioralACT:
        if user_id in self.behavioral_acts:
            return self.behavioral_acts[user_id]
        else:
            return self.default_behavioral_act