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

option: dict = {
    "model": Models.G2_FLASH_LITE
}

class Google(Base):

    def __init__(self):
        self._client = genai.Client()
        self._models = [m.value for m in Models]
        self._model = self._models[0]
        self._chats = self._client.chats.create(model=self._model)

    def reqMsg(self, msg):
        return self._req(msg)

    def reqFile(self, msg, file_path):
        f = self._client.files.upload(file = file_path)
        return self._req([msg, f])
    
    def reqImg(self, msg, img):
        return self._req([msg, img])

    def _req(self, cont) -> str:
        """Shared request method.

        Args:
            cont (any): request contents.

        Returns:
            str: response message.
        """
        result = "本日分のリクエストが上限になりました。"
        for m in self._models:
            try:
                response = self._chats.send_message(cont)
                result = response.text
            except errors.ClientError as e:
                if (e.status == "429"):
                    self._chats = self._client.chats.create(model=m, history=self._chats.get_history())
                    continue
                else:
                    result = f"予期せぬエラー: {e.message}"
                    break
            except e:
                result = f"予期せぬエラー: {e.message}"
                break

        return result

