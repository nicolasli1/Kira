from fastapi import FastAPI, HTTPException


app = FastAPI(title="mock-blockchain")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/tx/{txhash}")
async def get_transaction(txhash: str) -> dict:
    if txhash.endswith("confirmed") or txhash in {"0x123", "0xabc123confirmed"}:
        return {"txhash": txhash, "status": "confirmed"}
    if txhash.endswith("pending"):
        return {"txhash": txhash, "status": "pending"}
    raise HTTPException(status_code=404, detail="not found")
