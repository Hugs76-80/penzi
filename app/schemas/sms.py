from pydantic import BaseModel, ConfigDict, Field


class IncomingSMS(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sender: str = Field(alias="from", min_length=1)
    text: str


class Reply(BaseModel):
    to: str
    text: str


class SMSResult(BaseModel):
    replies: list[Reply]
