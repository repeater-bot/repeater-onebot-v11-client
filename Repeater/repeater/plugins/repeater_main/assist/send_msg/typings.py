from typing import Protocol
from nonebot.adapters.onebot.v11 import Message
from .sending_target import SendingTarget

class SEND_HOOK(Protocol):
    async def __call__(
        self,
        target: SendingTarget,
        message: Message
    ) -> bool | None:
        """
        Sending Hook

        :param target: Sending Target
        :param message: Sending Message
        :return: Blocks output when False is returned, and passes when True or None is returned.
        """
        pass

class RENDER_HOOK(Protocol):
    async def __call__(
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
        quality: int | None = None
    ) -> None:
        """
        Render Hook

        :param text: Text to render
        :param style: Style to render
        :param image_expiry_time: Image expiry time
        :param html_template: HTML template
        :param title: Title
        :param document_bottom_comment: Document bottom comment
        :param width: Width
        :param height: Height
        :param direct_output: Direct output
        :param no_pre_labels: No pre labels
        :param no_escape: No escape
        :param quality: Quality
        """
        pass