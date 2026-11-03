from fastapi import FastAPI

app = FastAPI(title="Penzi")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "penzi"}
