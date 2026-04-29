"""
Services
"""
from services.ai.base import Base as ai_base
from services.ai.google import Google as ai_google

def get_ai_service() -> ai_base:
    return ai_google()