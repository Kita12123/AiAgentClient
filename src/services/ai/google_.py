"""
Google AI Studio
https://googleapis.github.io/python-genai/
.env: GEMINI_API_KEY = <API KEY>
"""
from enum import Enum
from google import genai
from google.genai import errors

from services.ai.base import Base

# model name list. (Category: Text-out models)
# https://ai.google.dev/gemini-api/docs/models
class Models(Enum):
    G2_FLASH_LITE = "gemini-2.5-flash-lite"
    G2_FLASH = "gemini-2.5-flash"
    G3_FLASH_LITE = "gemini-3.1-flash-lite-preview"
    G3_FLASH = "gemini-3-flash-preview"

class Google(Base):

    def __init__(self):
        self._client = genai.Client()
        self._models = [m.value for m in Models]
        self._model = self._models[0]
        self._chats = self._client.chats.create(model=self._model)

    def request_message(self, msg):
        return self.__request(msg)

    def request_message_and_upload_file(self, msg, file_path):
        f = self._client.files.upload(file = file_path)
        return self.__request([msg, f])
    
    def request_message_with_image(self, msg, img):
        return self.__request([msg, img])

    def __request(self, cont) -> str:
        """Shared request method.

        Args:
            cont (any): request contents.

        Returns:
            str: response message.
        """
        default_result = "本日分のリクエストが上限になりました。"

        for model in self._models:
            try:
                # create a fresh chat for each model attempt to avoid re-using a potentially bad chat
                chats = self._client.chats.create(model=model)
                response = chats.send_message(cont)
                # Return immediately on first successful response to avoid duplicate sends
                return response.text
            except errors.ClientError as e:
                # Extract status code in a robust way
                status = getattr(e, "status", None) or getattr(e, "status_code", None) or getattr(e, "code", None)
                if str(status) == "429":
                    # Try next model
                    continue
                # Non-rate-limit client error: return its message
                return f"予期せぬエラー: {getattr(e, 'message', str(e))}"
            except Exception as e:
                # Catch-all for unexpected exceptions
                return f"予期せぬエラー: {str(e)}"

        # All models exhausted or rate-limited
        return default_result

