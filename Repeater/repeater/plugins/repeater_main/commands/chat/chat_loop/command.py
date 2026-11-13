import orjson
import asyncio
from contextlib import suppress
from ..._bases import BaseChat
from ....assist import PersonaInfo, SendMsg, Scene
from ....command_register import CommandCaller
from ....client_configs import storage_configs
from .session import ChatLoopSession

@CommandCaller.register
class ChatLoop(BaseChat):
    cmd = "chatLoop"
    aliases = {
        "clp",
        "CLP",
        "ChatLoop",
        "CHAT_LOOP"
    }
    description = f"""
        Talk to LLM and no longer need to `@bot`
        
        Usage:
        ```
        /{cmd}
        ```
    """

    def __init__(self):
        self.scenes_lock = asyncio.Lock()
        self.scenes: dict[Scene, PersonaInfo] = {}

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        async with self.scenes_lock:
            caller = self.scenes.get(persona_info.scene)
            if caller is not None:
                if caller.user_id != persona_info.user_id:
                    await send_msg.send_error(
                        f"This scene already has ChatLoop running from {orjson.dumps(caller.display_name).decode('utf-8')}({caller.user_id}), do not run it again."
                    )
                    return
                else:
                    await send_msg.send_error(
                        f"There is already a ChatLoop running in this scene. Do not run it again."
                    )
                    return
            self.scenes[persona_info.scene] = persona_info
        
        session = ChatLoopSession(persona_info, storage_configs.chat_loop)
        try:
            session.client = await self.get_client(persona_info)
            await session.start()
            await session.run()
        finally:
            # 场景登记必须在清理之后一定被摘掉：清理抛什么都不能让这个 scene 永久
            # 停在「已在运行」的状态里，否则重开会被自己挡住
            try:
                with suppress(asyncio.CancelledError):
                    await session.close()
            finally:
                async with self.scenes_lock:
                    self.scenes.pop(persona_info.scene, None)
