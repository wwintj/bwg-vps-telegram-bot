import logging
from typing import Any, Dict

import httpx

from app.config import KIWIVM_API_BASE, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)


class KiwiVMClient:
    def __init__(self, veid: str, api_key: str):
        self.veid = veid
        self.api_key = api_key
        self.base_params = {"veid": self.veid, "api_key": self.api_key}

    async def _request(self, method: str, **kwargs) -> Dict[str, Any]:
        url = f"{KIWIVM_API_BASE}/{method}"
        params = {**self.base_params, **kwargs}

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if data.get("error") != 0 and method != "getLiveServiceInfo":
                    logger.error(f"KiwiVM API error [{method}]: {data.get('message')}")

                return data
        except Exception as exc:
            logger.error(f"HTTP request failed for {method}: {exc}")
            return {"error": 1, "message": str(exc)}

    async def get_service_info(self) -> Dict[str, Any]:
        return await self._request("getServiceInfo")

    async def get_live_service_info(self) -> Dict[str, Any]:
        return await self._request("getLiveServiceInfo")

    async def execute_action(self, action: str) -> Dict[str, Any]:
        return await self._request(action)
