from sqlalchemy.orm import Session

from app.config import settings
from app.core import templates
from app.models.user import RegistrationStage
from app.schemas.sms import Reply
from app.services import registration
from app.services.registration import DetailsError, DetailsOutcome


def _message(outcome: DetailsOutcome, code: str) -> str:
    error = outcome.error
    user = outcome.user

    if error is None and user is not None:
        if user.registration_stage == RegistrationStage.COMPLETE:
            return templates.details_updated(code)
        return templates.ask_for_description(code)

    if error == DetailsError.NOT_REGISTERED:
        return templates.welcome(code)

    if error == DetailsError.FIELD_TOO_LONG:
        return templates.details_text_too_long()

    return templates.details_format_error(code)


def handle(db: Session, phone: str, args: list[str]) -> list[Reply]:
    outcome = registration.save_user_details(db, phone, args)
    return [Reply(to=phone, text=_message(outcome, settings.shortcode))]