from abc import ABC, abstractmethod


class VendorClient(ABC):
    name: str

    @abstractmethod
    async def send_transfer(self, amount: str, txhash: str) -> dict:
        raise NotImplementedError
