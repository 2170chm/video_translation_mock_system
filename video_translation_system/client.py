import time
import random
import logging
import requests
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ClientConfig:
    """Configuration for the translation status client"""
    # Initial delay between status checks (seconds)
    initial_delay: float = 1.0
    # Maximum delay between checks
    max_delay: float = 30.0
    # Factor to increase delay by after each check
    backoff_factor: float = 1.5
    # Maximum number of retries for failed requests
    max_retries: int = 3
    # Overall timeout for the entire process
    timeout: float = 300.0
    # Whether to add random jitter to delays
    jitter: bool = True

class TranslationError(Exception):
    """Exception for translation-related errors"""
    pass

class TranslationClient:
    def __init__(
        self,
        base_url: str,
        config: Optional[ClientConfig] = None,
        status_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """
        Initialize the translation client
        
        Args:
            base_url: Base URL of the translation server
            config: Optional client configuration
            status_callback: Optional callback for status updates
        """
        self.base_url = base_url.rstrip('/')
        self.config = config or ClientConfig()
        self.status_callback = status_callback
        self.session = requests.Session()
    
    def _get_status(self) -> Dict[str, Any]:
        """Make a single status check request"""
        response = self.session.get(f"{self.base_url}/status")
        # If the status code is not 200, raise an error
        if response.status_code != 200:
            raise TranslationError(f"Status check failed with code {response.status_code}")
        return response.json()
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for next attempt using exponential backoff"""
        # Calculate delay using exponential backoff with jitter
        # Clamp delay to max_delay
        delay = min(
            self.config.initial_delay * (self.config.backoff_factor ** attempt),
            self.config.max_delay
        )
        
        if self.config.jitter:
            delay *= (0.5 + random.random())
            
        return delay

    def wait_for_completion(self) -> Dict[str, Any]:
        """
        Wait for the translation job to complete
        
        Returns:
            Dict containing the final status response
        
        Raises:
            TranslationError: If the job fails or times out
        """
        start_time = time.time()
        attempt = 0
        
        while True:
            # Check if we've exceeded the overall timeout
            if time.time() - start_time > self.config.timeout:
                raise TranslationError("Translation job timed out")
            
            try:
                status = self._get_status()
                
                if self.status_callback:
                    self.status_callback(status)
                
                if status["result"] == "completed":
                    return status
                elif status["result"] == "error": # In case of error, raise an exception
                    raise TranslationError("Translation job failed")
                
                # Calculate and apply delay before next check
                delay = self._calculate_delay(attempt)
                logger.debug(f"Waiting {delay:.2f} seconds before next check")
                time.sleep(delay)
                attempt += 1
                
            except requests.RequestException as e: # In case of request error, retry up to max retries
                if attempt >= self.config.max_retries:
                    raise TranslationError(f"Max retries exceeded: {str(e)}")
                attempt += 1
                continue