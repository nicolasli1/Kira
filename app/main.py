import json
import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from app.blockchain import BlockchainClient, BlockchainVerificationError
from app.models import TransferRequest, TransferResponse
from app.vendor_registry import VendorRegistry


REQUEST_COUNTER = Counter(
    "transfer_requests_total",
    "Count of transfer requests by vendor and outcome",
    ["vendor", "outcome"],
)
VENDOR_LATENCY = Histogram(
    "vendor_request_latency_seconds",
    "Vendor request latency by vendor",
    ["vendor"],
)
TXHASH_CONFIRMATIONS = Counter(
    "txhash_verifications_total",
    "Txhash verification results",
    ["status"],
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "timestamp": self.formatTime(record, self.datefmt),
        }
        extra_keys = ["vendor", "txhash", "amount", "txhash_status", "vendor_status"]
        for key in extra_keys:
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(os.getenv("LOG_LEVEL", "INFO"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    yield


app = FastAPI(title="payments-api", lifespan=lifespan)
registry = VendorRegistry()
blockchain_client = BlockchainClient()
logger = logging.getLogger("payments-api")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/transfer", response_model=TransferResponse)
async def transfer(request: TransferRequest) -> TransferResponse:
    try:
        vendor = registry.get(request.vendor)
    except KeyError as exc:
        REQUEST_COUNTER.labels(vendor=request.vendor, outcome="unsupported_vendor").inc()
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        txhash_status = await blockchain_client.verify_txhash(request.txhash)
    except BlockchainVerificationError as exc:
        REQUEST_COUNTER.labels(vendor=request.vendor, outcome="blockchain_error").inc()
        raise HTTPException(status_code=502, detail="blockchain verification error") from exc

    TXHASH_CONFIRMATIONS.labels(status=txhash_status).inc()

    if txhash_status != "confirmed":
        REQUEST_COUNTER.labels(vendor=request.vendor, outcome="txhash_not_confirmed").inc()
        raise HTTPException(status_code=404, detail="txhash not found")

    start = time.perf_counter()
    vendor_response = await vendor.send_transfer(str(request.amount), request.txhash)
    VENDOR_LATENCY.labels(vendor=request.vendor).observe(time.perf_counter() - start)

    REQUEST_COUNTER.labels(vendor=request.vendor, outcome=vendor_response["status"]).inc()
    logger.info(
        "transfer processed",
        extra={
            "vendor": request.vendor,
            "txhash": request.txhash,
            "amount": str(request.amount),
            "txhash_status": txhash_status,
            "vendor_status": vendor_response["status"],
        },
    )

    return TransferResponse(
        vendor=request.vendor,
        txhash=request.txhash,
        amount=request.amount,
        txhash_status=txhash_status,
        vendor_response=vendor_response,
    )
