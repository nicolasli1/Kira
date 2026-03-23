from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_transfer_success_vendor_a() -> None:
    with patch("app.main.blockchain_client.verify_txhash", AsyncMock(return_value="confirmed")):
        response = client.post(
            "/transfer",
            json={"amount": 100, "vendor": "vendorA", "txhash": "0xabc123confirmed"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["vendor_response"]["status"] == "success"
    assert body["txhash_status"] == "confirmed"


def test_transfer_invalid_txhash() -> None:
    with patch("app.main.blockchain_client.verify_txhash", AsyncMock(return_value="not_found")):
        response = client.post(
            "/transfer",
            json={"amount": 100, "vendor": "vendorA", "txhash": "0xdeadbeef"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "txhash not found"


def test_transfer_unsupported_vendor() -> None:
    response = client.post(
        "/transfer",
        json={"amount": 100, "vendor": "vendorZ", "txhash": "0xabc123confirmed"},
    )

    assert response.status_code == 400
