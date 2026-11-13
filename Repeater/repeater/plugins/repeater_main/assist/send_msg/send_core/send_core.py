import time
import asyncio

from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.exception import (
    ActionFailed
)

from ...assist_func import (
    send_group_file,
    send_private_file,
)
from ...text_render.text_render import RendedImage
from ...scene import MessageSource
from ...namespace import Namespace
from ...text_render.text_render import TextRender
from ...response.response import Response
from typing import (
    Any
)
from ..sending_buffer_unit import SendingBufferUnit
from ....logger import logger as base_logger
from ..text_render_exceptions import (
    InvalidResponseData,
    RenderResponseException,
    NotInitializedResponse,
)
from ..zone_ugc_right import ZoneUGCRight
from .send_core_interface import BaseSendCore

logger = base_logger.bind(module = "SendMsg.SendCore")

class SendCore(BaseSendCore):
    async def render_text(
        self,
        text: str,
        style: str | None = None,
        image_expiry_time: int | None = None,
        html_template: str | None = None,
        title: str | None = None,
        document_bottom_comment: str | None = None,
        width: int | None = None,
        height: int | None = None,
        direct_output: bool | None = None,
        no_pre_labels: bool | None = None,
        no_escape: bool | None = None,
        quality: int | None = None,
        namespace: Namespace | None = None
    ) -> str:
        """
        渲染文本

        :param text: 渲染文本内容
        :param style: 渲染样式
        :param image_expiry_time: 图片过期时间
        :param html_template: HTML 模板
        :param title: 文档标题
        :param document_bottom_comment: 文档底部注释
        :param width: 图片宽度
        :param height: 图片高度
        :param direct_output: 是否直接输出
        :param no_pre_labels: 是否不添加标签
        :param no_escape: 是否不转义
        :param quality: 图片质量
        :param namespace: 命名空间
        :return: 渲染图片的 URL
        """
        user_configs = await self._persona_info.get_user_configs()
        text_render = TextRender(
            persona_info = self._persona_info,
            user_configs = user_configs,
            namespace = namespace
        )
        if text:
            if self._render_hook:
                tasks: list[asyncio.Task[None]] = [
                    asyncio.create_task(
                        hook(
                            text = text,
                            style = style,
                            image_expiry_time = image_expiry_time,
                            html_template = html_template,
                            title = title,
                            document_bottom_comment = document_bottom_comment,
                            width = width,
                            height = height,
                            direct_output = direct_output,
                            no_pre_labels = no_pre_labels,
                            no_escape = no_escape,
                            quality = quality,
                        )
                    )
                    for hook in self._render_hook
                ]
                await asyncio.gather(*tasks)
            
            render_response: Response[RendedImage] = await text_render.render(
                text = text,
                style = style,
                image_expiry_time = image_expiry_time,
                html_template = html_template,
                title = title,
                document_bottom_comment = document_bottom_comment,
                width = width,
                height = height,
                direct_output = direct_output,
                no_pre_labels = no_pre_labels,
                no_escape = no_escape,
                quality = quality
            )
            if render_response:
                data = render_response.get_data()
                if data is not None:
                    url = data.image_url
                    return url
                else:
                    logger.error(f"Render Data Is Invalid")
                    raise InvalidResponseData(render_response)
            elif render_response.initialized:
                raise NotInitializedResponse(render_response)
            else:
                raise RenderResponseException(render_response)
        else:
            raise ValueError("Text is empty.")
    
    async def send_to_queue(
        self,
        message: str | Message | MessageSegment,
        reply: bool = True,
        break_code: int = 0,
        continue_handler: bool = False,
        *args,
        **kwargs
    ) -> None:
        """
        发送消息到队列

        :param message: 消息对象
        """
        now = time.time_ns()
        monotonic_now = time.perf_counter_ns()
        await self._buffer.put(
            SendingBufferUnit(
                message = message,
                args = args,
                kwargs = kwargs,
                time = now,
                monotonic_time = monotonic_now,
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler,
            )
        )
    
    async def send_to_matcher(
        self,
        message: str | Message | MessageSegment,
        reply: bool = True,
        break_code: int = 0,
        continue_handler: bool = False,
        *args,
        **kwargs
    ) -> None:
        """
        发送消息到 Matcher

        :param message: 消息对象
        """
        if self._matcher is not None:
            await self._matcher.send(
                message,
                *args,
                **kwargs
            )
    
    async def send_to_api(
        self,
        message: str | Message | MessageSegment,
        reply: bool = True,
        break_code: int = 0,
        continue_handler: bool = False,
        *args,
        **kwargs
    ) -> None:
        """
        发送消息到 API

        :param message: 消息对象
        """
        if isinstance(message, MessageSegment):
            message = Message(
                message
            )
        bot = self._persona_info.cached_api
        if self._target is not None:
            target = self._target
        else:
            target = self._persona_info.scene
        
        if target.id is None:
            raise ValueError(
                "Set target, but no target id provided."
            )
        
        if target.is_private:
            await bot.send_private_msg(
                user_id = int(target.id),
                message = message,
                *args,
                **kwargs
            )
        elif target.is_group:
            await bot.send_group_msg(
                group_id = int(target.id),
                message = message,
                *args,
                **kwargs
            )
    
    async def _send_file(
            self,
            url: str,
            file_name: str
        ) -> str | None:
        """
        发送文件

        :param url: 文件URL
        :param file_name: 文件名
        """
        target = self._target or self._persona_info.scene
        if target.id is None:
            raise ValueError('target.id is None')
        try:
            match target.source:
                case MessageSource.GROUP:
                    return await send_group_file(
                        bot = self._persona_info.cached_api,
                        group_id = target.id,
                        url = url,
                        file_name = file_name
                    )
                case MessageSource.PRIVATE:
                    return await send_private_file(
                        bot = self._persona_info.cached_api,
                        user_id = target.id,
                        url = url,
                        file_name = file_name
                    )
        except ActionFailed as e:
            logger.error(f"Failed to upload file: {e}")
            raise
    
    async def _send_poke(
            self,
            namespace: Namespace,
        ) -> None:
        """
        发送戳一戳
        """
        match namespace.mode:
            case MessageSource.GROUP:
                if self._persona_info.group_id is not None:
                    if namespace.group_id is None:
                        raise ValueError("group_id is None")
                    
                    await self._persona_info.cached_api.send_poke(
                        group_id = namespace.group_id,
                        user_id = namespace.user_id
                    )
            case MessageSource.PRIVATE:
                await self._persona_info.cached_api.send_poke(
                    user_id = namespace.user_id
                )
            case _:
                raise ValueError("Invalid message source")

    async def _send_zone(
            self,
            content: str,
            images: list[str] | None = None,
            ugc_right: ZoneUGCRight | None = None,
            target_uins: list[int] | None = None,
        ) -> str | None:
        """
        发送 QQ 空间说说

        :param content: 说说内容
        :param images: 图片链接列表
        :param ugc_right: 权限
        :param target_uins: 目标用户列表
        """

        data: dict[str, Any] = {
            "content": content
        }

        if images:
            data["images"] = images

        if ugc_right:
            data["ugc_right"] = ugc_right.to_zone_ugc_right_num()

        if target_uins:
            data["target_uins"] = target_uins

        response: dict = await self._persona_info.cached_api.send_qzone_msg(
            **data
        )

        return response.get("tid")