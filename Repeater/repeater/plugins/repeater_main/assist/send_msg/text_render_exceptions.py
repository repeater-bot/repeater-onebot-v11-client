from ..response import Response

class TextRenderException(Exception):
    """Base class for exceptions in text_render module."""
    pass

class RenderResponseException(TextRenderException):
    """Exception raised for errors in the render response."""
    def __init__(self, response: Response):
        self.response = response
        self.message: str = "Render response error, response not initialized"
        if response:
            self.message = f"Render response error: {self.response.text}"
        super().__init__(self.message)


class InvalidResponseData(RenderResponseException):
    """Exception raised for errors in the render response data."""
    pass

class NotInitializedResponse(RenderResponseException):
    """Exception raised for errors in the render response data."""
    pass