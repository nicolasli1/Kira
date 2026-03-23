from app.vendors.base import VendorClient


class VendorAClient(VendorClient):
    name = "vendorA"

    async def send_transfer(self, amount: str, txhash: str) -> dict:
        return {"status": "success", "amount": amount, "reference": f"a-{txhash[-6:]}"}
