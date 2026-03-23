from app.vendors.vendor_a import VendorAClient
from app.vendors.vendor_b import VendorBClient


class VendorRegistry:
    def __init__(self) -> None:
        self._vendors = {
            VendorAClient.name: VendorAClient(),
            VendorBClient.name: VendorBClient(),
        }

    def get(self, vendor_name: str):
        vendor = self._vendors.get(vendor_name)
        if vendor is None:
            raise KeyError(f"Unsupported vendor: {vendor_name}")
        return vendor
