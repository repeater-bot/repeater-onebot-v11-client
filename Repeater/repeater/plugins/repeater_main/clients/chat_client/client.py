import re
import uuid
import asyncio

from typing import (
    Any
)
from .chat_buffer import ChatBufferResponse
from ..content_role import ContentRole
from .response_body import ChatResponse
from .break_response_body import BreakResponse
from .cross_user_data_routing import CrossUserDataRouting
from ...assist import Response, BaseClient
from ..content_unit import ContentUnit
from ...client_configs import *
from .request_model import ChatRequestModel, ChatUserInfo, AdditionalData
from ..._adaptation_info import __adaptation__, __adaptation_text__
from ...logger import logger as base_logger
from ...exceptions import BreakWithErrorMessage
from ..status_client import StatusClient

logger = base_logger.bind(module = "chat_client")

class ChatClient(BaseClient):
    metadata_pattern = re.compile(r"> Message\s*?Metadata:.*?---(?:\r?\n)+", re.DOTALL | re.IGNORECASE)
    timeout = storage_configs.server_api_timeout.chat

    def __post_init__(self):
        self.status_client = StatusClient(
            persona_info = self._persona_info,
            user_configs = self.user_configs,
            namespace = self._namespace,
        )
    
    @property
    def merge_namespace(self) -> str | None:
        if storage_configs.usage_group_context:
            return self._persona_info.namespace.merge_namespace
        return None
    
    def _add_extra_template_fields(self, extra_template_fields: dict[str, Any] | None = None) -> dict[str, Any]:
        if extra_template_fields is None:
            extra_template_fields_copy = {}
        else:
            extra_template_fields_copy = extra_template_fields.copy()
        extra_template_fields_copy.update(
            {
                "message_type": self._persona_info.source.value,
                "adaptation_version": __adaptation__,
                "adaptation_info": __adaptation_text__,
            }
        )
        return extra_template_fields_copy
    
    async def send_message(
        self,
        message: str | None = None,
        suffix: str | None = None,
        echo: bool | None = None,
        fim_mode: bool | None = None,
        role_name: str | None = None,
        temporary_prompt: str | None = None,
        history_messages: list[ContentUnit] | None = None,
        model_id: str | None = None,
        thinking: bool | None = None,
        allow_tool_calls: bool | None = None,
        extra_template_fields: dict[str, Any] | None = None,
        image_url: str | list[str] | None = None,
        video_url: str | list[str] | None = None,
        audio_url: str | list[str] | None = None,
        file_url: str | list[str] | None = None,
        load_prompt: bool | None = None,
        save_context: bool | None = None,
        save_new_only: bool | None = None,
        history_msg_role_map: dict[ContentRole, ContentRole | None] | None = None,
        cross_user_data_routing: CrossUserDataRouting | None = None,
        continue_completion: bool | None = None,
        timeout: int | float | None = None,
        raw_message: bool = False,
    ) -> Response[ChatResponse]:
        """
        发送消息到AI后端
        
        :param message: 消息内容
        :param suffix: 消息后缀
        :param echo: 是否回显
        :param fim_mode: 是否使用 fim 模式
        :param role_name: 角色名称
        :param temporary_prompt: 临时提示
        :param history_messages: 历史消息
        :param model_id: 模型UID
        :param thinking: 思考模式
        :param allow_tool_calls: 是否允许工具调用
        :param extra_template_fields: 额外模板字段
        :param image_url: 图片URL
        :param video_url: 视频URL
        :param audio_url: 音频URL
        :param file_url: 文件URL
        :param load_prompt: 是否加载提示
        :param save_context: 是否保存上下文
        :param save_new_only: 是否只保存新内容
        :param history_msg_role_map: 历史消息角色映射
        :param cross_user_data_routing: 跨用户数据路由
        :param continue_completion: 是否继续生成
        :param raw_message: 是否直接提交原始数据
        :return: AI返回的消息
        """
        task_id = uuid.uuid4()
        url = self.join_url_static(CHAT_ROUTE, self.namespace)

        if cross_user_data_routing is None:
            if self.merge_namespace:
                cross_user_data_routing = CrossUserDataRouting()
                cross_user_data_routing.context.fill_missing(self.merge_namespace)
        
        extra_template_fields = self._add_extra_template_fields(extra_template_fields)

        data = ChatRequestModel(
            message = message,
            task_id = str(task_id),
            suffix = suffix,
            echo = echo,
            fim_mode = fim_mode,
            user_info = ChatUserInfo(
                username = self._persona_info.nickname,
                nickname = self._persona_info.card,
                gender = self._persona_info.gender,
                age = self._persona_info.age,
            ),
            add_metadata = not raw_message,
            role_name = role_name,
            temporary_prompt = temporary_prompt,
            history_messages = history_messages,
            model_id = model_id,
            thinking = thinking,
            allow_tool_calls = allow_tool_calls,
            extra_template_fields = extra_template_fields,
            additional_data = AdditionalData(
                image_url = image_url,
                video_url = video_url,
                audio_url = audio_url,
                file_url = file_url,
            ),
            load_prompt = load_prompt,
            save_context = save_context,
            save_new_only = save_new_only,
            history_msg_role_map = history_msg_role_map,
            cross_user_data_routing = cross_user_data_routing,
            continue_completion = continue_completion,
        )
        
        if timeout is None:
            timeout = storage_configs.model_first_chunk_timeout
        
        data.inject_metadata()
        
        task = asyncio.create_task(
            self.client.post(
                url = url,
                json = data.model_dump(exclude_none = True),
            )
        )

        last_buffer_length: int | None = None
        if timeout is not None:
            while True:
                try:
                    response = await asyncio.wait_for(
                        fut = asyncio.shield(
                            task
                        ),
                        timeout = timeout
                    )
                    break
                except asyncio.TimeoutError:
                    buffer_response = await self.get_chat_buffer()
                    if buffer_response:
                        buffer = buffer_response.get_data()
                        if buffer is not None:
                            now_task_buffer = buffer.buffers.get(str(task_id))
                            if now_task_buffer is None:
                                continue
                            if last_buffer_length is None:
                                if last_buffer_length == 0:
                                    await self._abnormal_status(
                                        "The build task has been actively aborted because the buffer did not find anything.",
                                        task_id = str(task_id),
                                    )
                            else:
                                now_buffer_length = len(buffer)
                                if now_buffer_length == last_buffer_length:
                                    await self._abnormal_status(
                                        "The build task has been actively aborted because this check buffer is the same length as the last time.",
                                        task_id = str(task_id),
                                    )
                                else:
                                    last_buffer_length = now_buffer_length
        response = await task
        
        return Response(
            response,
            ChatResponse
        )
    
    async def _abnormal_status(self, message: str, task_id: str | None = None) -> None:
        response = await self.status_client.get_client_task_status(self.namespace)
        if response:
            data = response.get_data()
            if data is not None:
                stack = data.tasks
            for task in stack:
                if "Calling Tools" in task:
                    return
        
        await self.break_chat_task(task_id)
        raise BreakWithErrorMessage(2, message)
    
    async def break_chat_task(self, task_id: str | None = None) -> Response[BreakResponse]:
        """
        中断当前在线的任务
        """
        try:
            if task_id is None:
                response = await self.client.post(
                    url = self.join_url_static(BREAK_CHAT_TASK_ROUTE, self.namespace)
                )
            else:
                response = await self.client.post(
                    url = self.join_url_static(BREAK_CHAT_TASK_ROUTE, self.namespace, task_id)
                )
        except Exception as e:
            logger.error(
                "Error sending message to chat core: {error}",
                error = e
            )
            return Response(model=BreakResponse)

        return Response(
            httpx_response = response,
            model = BreakResponse
        )
    
    async def get_chat_buffer(self) -> Response[ChatBufferResponse]:
        """
        获取当前聊天缓冲区
        """
        try:
            response = await self.client.get(
                url = self.join_url_static(GET_CHAT_BUFFER_ROUTE, self.namespace)
            )
        except Exception as e:
            logger.error(
                "Error sending message to chat core: {error}",
                error = e
            )
            return Response(model=ChatBufferResponse)

        return Response(
            httpx_response = response,
            model = ChatBufferResponse
        )