"""
Services package for Deep-Shiva API
Contains business logic and external service integrations
"""

from .ollama_service import ollama_service

__all__ = ["ollama_service"]