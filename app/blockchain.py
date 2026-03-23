import os

import httpx


class BlockchainVerificationError(Exception):
    pass


class BlockchainClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("BLOCKCHAIN_SERVICE_URL", "http://localhost:8001")

    async def verify_txhash(self, txhash: str) -> str:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{self.base_url}/tx/{txhash}")

        if response.status_code == 404:
            return "not_found"

        if response.status_code != 200:
            raise BlockchainVerificationError("blockchain verification failed")

        payload = response.json()
        return payload["status"]
