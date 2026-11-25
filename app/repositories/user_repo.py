from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import RegistrationStage, User
from app.utils.phone import normalize_phone

_STAGES = list(RegistrationStage)


def _require_stored_format(phone: str) -> None:
    if normalize_phone(phone) != phone:
        raise ValueError(f"Phone must be in stored format 2547XXXXXXXX, got {phone!r}")


def _advance_stage(user: User, stage: RegistrationStage) -> None:
    current = RegistrationStage(user.registration_stage)
    if _STAGES.index(current) < _STAGES.index(stage):
        user.registration_stage = stage.value


def get_by_phone(db: Session, phone: str) -> User | None:
    _require_stored_format(phone)
    return db.scalar(select(User).where(User.phone == phone))


def create(
    db: Session,
    phone: str,
    name: str,
    age: int,
    gender: str,
    county: str,
    town: str,
) -> User:
    _require_stored_format(phone)
    user = User(
        phone=phone,
        name=name,
        age=age,
        gender=gender,
        county=county,
        town=town,
        registration_stage=RegistrationStage.STARTED.value,
    )
    db.add(user)
    db.flush()
    return user


def save_details(
    db: Session,
    user: User,
    education: str,
    profession: str,
    marital_status: str,
    religion: str,
    ethnicity: str,
) -> User:
    user.education = education
    user.profession = profession
    user.marital_status = marital_status
    user.religion = religion
    user.ethnicity = ethnicity
    _advance_stage(user, RegistrationStage.DETAILS_DONE)
    db.flush()
    return user


def save_description(db: Session, user: User, description: str) -> User:
    user.description = description
    _advance_stage(user, RegistrationStage.COMPLETE)
    db.flush()
    return user