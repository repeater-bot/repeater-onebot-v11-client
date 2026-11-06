from ...client_configs import *
from ..response.response import Response
from .request import RenderRequest
from .response import RendedImage
from ..base_client import BaseClient

class TextRender(BaseClient):
    timeout = storage_configs.server_api_timeout.render
    
    async def render(
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
        ) -> Response[RendedImage]:
        
        render_request = RenderRequest(
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
        response = await self.client.post(
            self.join_url_static(TEXT_RENDER_ROUTE, self.namespace),
            json = render_request.model_dump(exclude_none = True)
        )
        
        return Response(
            response,
            model = RendedImage
        )
        