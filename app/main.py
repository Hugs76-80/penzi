from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db

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


@app.get("/api/db-check")
def db_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "connected"}