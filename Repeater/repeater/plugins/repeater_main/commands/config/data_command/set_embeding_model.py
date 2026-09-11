from ....assist import PersonaInfo, SendMsg, Response
from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import BaseConfig


@CommandCaller.register
class SetEmbeddingModel(BaseConfig):
    cmd = "setEmbeddingModel"
    aliases = {
        "sem",
        "SEM",
        "set_embedding_model",
        "Set_Embedding_Model",
        "SetEmbeddingModel",
        "SET_EMBEDING_MODEL",
    }
    field = "embedding_model_id"
    description = f"""
    Set up a model for generating embeddings.

    Usage:
      /{cmd} model_id
    """
    
    async def finish_message(
            self,
            persona_info: PersonaInfo,
            send_msg: SendMsg,
            response: Response,
            field: str,
            value: str
        ):
        await send_msg.send_response_check_code(response, f"Set Embedding Model to {value}")