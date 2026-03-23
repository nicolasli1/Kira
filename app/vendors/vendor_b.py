from app.vendors.base import VendorClient


class VendorBClient(VendorClient):
    name = "vendorB"

    async def send_transfer(self, amount: str, txhash: str) -> dict:
        return {"status": "pending", "amount": amount, "reference": f"b-{txhash[-6:]}"}
