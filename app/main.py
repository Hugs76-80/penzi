from fastapi import FastAPI

from app.config import settings

app = FastAPI(title="Penzi")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "penzi"}


@app.get("/api/config-check")
def config_check():
    return {
        "shortcode": settings.shortcode,
        "sms_gateway": settings.sms_gateway,
        "database_url_loaded": bool(settings.database_url),
        "onfon_key_set": bool(settings.onfon_api_key),
    }