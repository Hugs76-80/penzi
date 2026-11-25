from sqlalchemy.orm import Session

from app.config import settings
from app.core import templates
from app.models.user import RegistrationStage
from app.schemas.sms import Reply
from app.services import registration
from app.services.registration import MAX_AGE, MIN_AGE, StartError, StartOutcome

_ALREADY_REGISTERED = {
    RegistrationStage.STARTED: templates.already_registered_started,
    RegistrationStage.DETAILS_DONE: templates.already_registered_details_done,
    RegistrationStage.COMPLETE: templates.already_registered_complete,
}


def _message(outcome: StartOutcome, code: str) -> str:
    error = outcome.error
    user = outcome.user

    if error is None and user is not None:
        return templates.profile_created(user.name or "", code)

    if error == StartError.ALREADY_REGISTERED and user is not None:
        stage = RegistrationStage(user.registration_stage)
        return _ALREADY_REGISTERED[stage](user.name or "", code)

    if error in (StartError.AGE_NOT_A_NUMBER, StartError.AGE_OUT_OF_RANGE):
        return templates.invalid_age(MIN_AGE, MAX_AGE)

    if error == StartError.INVALID_GENDER:
        return templates.invalid_gender()

    if error == StartError.FIELD_TOO_LONG:
        return templates.start_text_too_long()

    return templates.start_format_error(code)


def handle(db: Session, phone: str, args: list[str]) -> list[Reply]:
    outcome = registration.start_registration(db, phone, args)
    return [Reply(to=phone, text=_message(outcome, settings.shortcode))]