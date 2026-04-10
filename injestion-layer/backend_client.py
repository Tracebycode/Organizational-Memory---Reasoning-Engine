"""
Backend API Client.

Sends structured decision payloads to the backend's
POST /store-decision endpoint.
"""

import logging
from typing import Any, Dict

import httpx

from schema import DecisionPayload

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default backend configuration
# ---------------------------------------------------------------------------
BACKEND_BASE_URL = "http://localhost:8000"


class BackendClient:
    """Async HTTP client for the Organizational Memory backend."""

    def __init__(
        self,
        base_url: str = BACKEND_BASE_URL,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def store_decision(self, payload: DecisionPayload) -> Dict[str, Any]:
        """
        POST a structured decision to the backend.

        Args:
            payload: Validated DecisionPayload to send.

        Returns:
            The JSON response body from the backend.

        Raises:
            BackendError: If the backend is unreachable or returns an error.
        """
        url = f"{self.base_url}/store-decision"
        body = payload.model_dump()

        logger.info("Sending decision to backend: %s", url)
        logger.debug("Payload: %s", body)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=body)
                response.raise_for_status()
                result = response.json()
                logger.info("Backend response: %s", result)
                return result

        except httpx.ConnectError:
            raise BackendError(
                f"Cannot connect to the backend at {self.base_url}. "
                "Ensure the backend server is running."
            )
        except httpx.HTTPStatusError as exc:
            raise BackendError(
                f"Backend returned HTTP {exc.response.status_code}: "
                f"{exc.response.text}"
            )
        except Exception as exc:
            raise BackendError(f"Backend request failed: {exc}")

    async def health_check(self) -> bool:
        """Ping the backend root endpoint to verify connectivity."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/")
                return response.status_code == 200
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class BackendError(Exception):
    """Raised when communication with the backend fails."""
    pass
