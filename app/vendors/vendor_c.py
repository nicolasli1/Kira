from app.vendors.base import VendorClient


class VendorCClient(VendorClient):
    name = "vendorC"

    async def send_transfer(self, amount: str, txhash: str) -> dict:
        return {"status": "queued", "amount": amount, "reference": f"c-{txhash[-6:]}"}
