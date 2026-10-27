"""HTTP client for communicating with Evershade services.

Provides a synchronous httpx client with Bearer token authentication
and proper error handling.
"""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class ServiceClient:
    """HTTP client for an Evershade service."""

    def __init__(
        self, base_url: str, api_key: str | None = None, timeout: float = 10.0
    ):
        """Initialize the service client.

        Args:
            base_url: Base URL of the service.
            api_key: Optional Bearer token for authentication.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        """Build request headers."""
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def get(self, path: str, **params: Any) -> dict | None:
        """Make a GET request.

        Args:
            path: API path (e.g., '/health').
            **params: Query parameters.

        Returns:
            Parsed JSON response or None on failure.
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(
                    f"{self.base_url}{path}",
                    headers=self._headers(),
                    params=params,
                )
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 401:
                    logger.warning(f"Unauthorized access to {self.base_url}{path}")
                    return None
                elif resp.status_code == 403:
                    logger.warning(f"Forbidden access to {self.base_url}{path}")
                    return None
                elif resp.status_code == 503:
                    logger.warning(f"Service unavailable: {self.base_url}{path}")
                    return None
                else:
                    logger.error(f"HTTP {resp.status_code} from {self.base_url}{path}")
                    return None
        except httpx.ConnectError:
            logger.warning(f"Cannot connect to {self.base_url}")
            return None
        except httpx.TimeoutException:
            logger.warning(f"Timeout connecting to {self.base_url}{path}")
            return None
        except Exception as e:
            logger.error(f"Error requesting {self.base_url}{path}: {e}")
            return None

    def post(self, path: str, json_data: dict | None = None) -> dict | None:
        """Make a POST request.

        Args:
            path: API path.
            json_data: Optional JSON body.

        Returns:
            Parsed JSON response or None on failure.
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    f"{self.base_url}{path}",
                    headers=self._headers(),
                    json=json_data,
                )
                if resp.status_code in (200, 201):
                    return resp.json()
                else:
                    logger.error(f"HTTP {resp.status_code} from {self.base_url}{path}")
                    return None
        except httpx.ConnectError:
            logger.warning(f"Cannot connect to {self.base_url}")
            return None
        except httpx.TimeoutException:
            logger.warning(f"Timeout connecting to {self.base_url}{path}")
            return None
        except Exception as e:
            logger.error(f"Error requesting {self.base_url}{path}: {e}")
            return None

    def check_health(self) -> dict:
        """Check service health.

        Returns:
            Dict with 'healthy' (bool) and 'data' (response or None).
        """
        data = self.get("/health")
        return {"healthy": data is not None, "data": data}

    def check_capabilities(self) -> dict:
        """Check service capabilities.

        Returns:
            Dict with 'available' (bool) and 'data' (response or None).
        """
        data = self.get("/api/capabilities")
        return {"available": data is not None, "data": data}
