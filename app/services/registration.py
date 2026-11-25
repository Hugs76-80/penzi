from dataclasses import dataclass
from enum import StrEnum

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories import user_repo

MIN_AGE = 18
MAX_AGE = 99
NAME_MAX = 100
COUNTY_MAX = 50
TOWN_MAX = 50
_GENDERS = {"male": "Male", "female": "Female"}


class StartError(StrEnum):
    WRONG_FIELD_COUNT = "wrong_field_count"
    MISSING_FIELD = "missing_field"
    FIELD_TOO_LONG = "field_too_long"
    AGE_NOT_A_NUMBER = "age_not_a_number"
    AGE_OUT_OF_RANGE = "age_out_of_range"
    INVALID_GENDER = "invalid_gender"
    ALREADY_REGISTERED = "already_registered"


@dataclass(frozen=True)
class StartOutcome:
    error: StartError | None = None
    user: User | None = None


def _clean(text: str) -> str:
    return " ".join(text.split())


def _check_text(value: str, max_length: int) -> StartError | None:
    if not value:
        return StartError.MISSING_FIELD
    if len(value) > max_length:
        return StartError.FIELD_TOO_LONG
    return None


def start_registration(db: Session, phone: str, fields: list[str]) -> StartOutcome:
    existing = user_repo.get_by_phone(db, phone)
    if existing is not None:
        return StartOutcome(StartError.ALREADY_REGISTERED, existing)

    if len(fields) != 5:
        return StartOutcome(StartError.WRONG_FIELD_COUNT)
    name, age_text, gender_text, county, town = (_clean(f) for f in fields)

    problem = _check_text(name, NAME_MAX)
    if problem:
        return StartOutcome(problem)

    if not (age_text.isascii() and age_text.isdigit()):
        return StartOutcome(StartError.AGE_NOT_A_NUMBER)
    if len(age_text) > 3:
        return StartOutcome(StartError.AGE_OUT_OF_RANGE)
    age = int(age_text)
    if not MIN_AGE <= age <= MAX_AGE:
        return StartOutcome(StartError.AGE_OUT_OF_RANGE)

    gender = _GENDERS.get(gender_text.lower())
    if gender is None:
        return StartOutcome(StartError.INVALID_GENDER)

    problem = _check_text(county, COUNTY_MAX) or _check_text(town, TOWN_MAX)
    if problem:
        return StartOutcome(problem)

    try:
        with db.begin_nested():
            user = user_repo.create(
                db,
                phone=phone,
                name=name,
                age=age,
                gender=gender,
                county=county,
                town=town,
            )
    except IntegrityError:
        winner = user_repo.get_by_phone(db, phone)
        if winner is None:
            raise
        return StartOutcome(StartError.ALREADY_REGISTERED, winner)
    return StartOutcome(user=user)