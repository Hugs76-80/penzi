from fastapi import APIRouter

from app.schemas.sms import IncomingSMS, Reply, SMSResult

router = APIRouter(prefix="/api/sms", tags=["sms"])


@router.post("/incoming", response_model=SMSResult)
def incoming_sms(sms: IncomingSMS):
    reply = Reply(to=sms.sender, text=f"Echo: {sms.text}")
    return SMSResult(replies=[reply])