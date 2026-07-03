"""
Configuration for Google Gemini API integration.

This module provides configuration management for the AI integration layer,
including API credentials, model settings, and rate limiting parameters.
"""

import os
from dataclasses import dataclass
from typing import Optional
import streamlit as st
from src.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GeminiConfig:
    """Configuration for Gemini API."""
    
    api_key: str
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_tokens: int = 2048
    requests_per_minute: int = 10
    timeout_seconds: int = 30
    
    @classmethod
    def from_environment(cls) -> Optional['GeminiConfig']:
        """
        Load Gemini API configuration from environment variables or Streamlit secrets.
        
        Priority order:
        1. Streamlit secrets (st.secrets)
        2. Environment variables
        
        Returns:
            GeminiConfig if credentials found, None otherwise
        """
        api_key = None
        
        # Try Streamlit secrets first
        try:
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                api_key = st.secrets['GEMINI_API_KEY']
                logger.info("Loaded Gemini API key from Streamlit secrets")
        except Exception as e:
            logger.debug(f"Could not load from Streamlit secrets: {e}")
        
        # Fallback to environment variables
        if not api_key:
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key:
                logger.info("Loaded Gemini API key from environment variables")
        
        if not api_key:
            logger.warning("Gemini API key not found in secrets or environment variables")
            return None
        
        # Load optional configuration parameters
        model_name = os.environ.get('GEMINI_MODEL_NAME', 'gemini-1.5-flash')
        temperature = float(os.environ.get('GEMINI_TEMPERATURE', '0.7'))
        max_tokens = int(os.environ.get('GEMINI_MAX_TOKENS', '2048'))
        requests_per_minute = int(os.environ.get('GEMINI_RATE_LIMIT', '10'))
        
        return cls(
            api_key=api_key,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            requests_per_minute=requests_per_minute
        )
    
    def validate(self) -> bool:
        """
        Validate configuration parameters.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.api_key or len(self.api_key.strip()) == 0:
            logger.error("API key is empty or invalid")
            return False
        
        if self.temperature < 0 or self.temperature > 1:
            logger.error(f"Temperature {self.temperature} out of valid range [0, 1]")
            return False
        
        if self.max_tokens < 1:
            logger.error(f"Max tokens {self.max_tokens} must be positive")
            return False
        
        if self.requests_per_minute < 1:
            logger.error(f"Requests per minute {self.requests_per_minute} must be positive")
            return False
        
        return True
