import unittest
from unittest.mock import patch, Mock
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import services.ai.google_ as google_mod

class CustomClientError(Exception):
    def __init__(self, status=None, message=""):
        self.status = status
        self.message = message
        super().__init__(message)

class TestGoogleAI(unittest.TestCase):

    def setUp(self):
        # Patch the genai Client before instantiating Google
        self.patcher = patch('services.ai.google_.genai.Client')
        self.mock_client_cls = self.patcher.start()
        self.addCleanup(self.patcher.stop)

        # Replace the module's ClientError with our custom exception for controlled behavior
        self.orig_client_error = google_mod.errors.ClientError
        google_mod.errors.ClientError = CustomClientError

    def tearDown(self):
        google_mod.errors.ClientError = self.orig_client_error

    def _make_client_with_chats(self, chat_map, files_upload_return=None):
        """Helper: chat_map is dict model->chat_mock"""
        mock_client = Mock()
        def create(model=None):
            return chat_map.get(model, Mock())
        # chats.create should return an object with send_message
        mock_client.chats.create.side_effect = create
        mock_client.files.upload.return_value = files_upload_return
        self.mock_client_cls.return_value = mock_client
        return mock_client

    def test_request_message_success(self):
        chat = Mock()
        chat.send_message.return_value = Mock(text='hello')
        # map all models to the same chat
        chat_map = {m.value: chat for m in google_mod.Models}
        self._make_client_with_chats(chat_map)

        g = google_mod.Google()
        res = g.request_message('hi')
        self.assertEqual(res, 'hello')

    def test_request_message_and_upload_file_calls_upload(self):
        chat = Mock()
        chat.send_message.return_value = Mock(text='file-response')
        chat_map = {m.value: chat for m in google_mod.Models}
        mock_client = self._make_client_with_chats(chat_map, files_upload_return='uploaded')

        g = google_mod.Google()
        res = g.request_message_and_upload_file('hi','/tmp/x')
        # files.upload should have been called with file argument
        mock_client.files.upload.assert_called_with(file='/tmp/x')
        self.assertEqual(res, 'file-response')

    def test_rate_limit_then_success(self):
        # First model will raise 429, second will succeed
        models = list(google_mod.Models)
        first_model = models[0].value
        second_model = models[1].value

        chat1 = Mock()
        chat1.send_message.side_effect = CustomClientError(status='429', message='rate')
        chat2 = Mock()
        chat2.send_message.return_value = Mock(text='second-ok')

        chat_map = {first_model: chat1, second_model: chat2}
        # Map remaining models to a chat that would raise 429 to be safe
        for m in google_mod.Models:
            chat_map.setdefault(m.value, chat1)

        self._make_client_with_chats(chat_map)
        g = google_mod.Google()
        res = g.request_message('hi')
        self.assertEqual(res, 'second-ok')

    def test_non_429_client_error_returns_message(self):
        chat = Mock()
        chat.send_message.side_effect = CustomClientError(status='500', message='server oops')
        chat_map = {m.value: chat for m in google_mod.Models}
        self._make_client_with_chats(chat_map)

        g = google_mod.Google()
        res = g.request_message('hi')
        self.assertIn('予期せぬエラー', res)
        self.assertIn('server oops', res)

    def test_generic_exception_returns_message(self):
        chat = Mock()
        chat.send_message.side_effect = ValueError('boom')
        chat_map = {m.value: chat for m in google_mod.Models}
        self._make_client_with_chats(chat_map)

        g = google_mod.Google()
        res = g.request_message('hi')
        self.assertIn('予期せぬエラー', res)
        self.assertIn('boom', res)

    def test_all_models_rate_limited_returns_default(self):
        chat = Mock()
        chat.send_message.side_effect = CustomClientError(status='429', message='rate')
        chat_map = {m.value: chat for m in google_mod.Models}
        self._make_client_with_chats(chat_map)

        g = google_mod.Google()
        res = g.request_message('hi')
        self.assertEqual(res, '本日分のリクエストが上限になりました。')

if __name__ == '__main__':
    unittest.main()
