import pytest
from sqlalchemy import func, select

from app.models.user import RegistrationStage, User
from app.repositories import user_repo
from app.services import registration
from app.services.registration import StartError

PHONE = "254712345678"
FIELDS = ["Jamal Jalang'o", "29", "Male", "Mombasa", "Bamburi"]


def fields_with(index, value):
    changed = list(FIELDS)
    changed[index] = value
    return changed


def count_users(db):
    return db.scalar(select(func.count()).select_from(User))


def test_valid_registration_creates_a_started_user(db):
    outcome = registration.start_registration(db, PHONE, FIELDS)
    assert outcome.error is None
    user = outcome.user
    assert user is not None
    assert user.phone == PHONE
    assert user.name == "Jamal Jalang'o"
    assert user.age == 29
    assert user.gender == "Male"
    assert user.county == "Mombasa"
    assert user.town == "Bamburi"
    assert user.registration_stage == RegistrationStage.STARTED
    assert count_users(db) == 1


def test_extra_spaces_in_fields_are_cleaned(db):
    messy = ["  Jamal   Jalang'o ", " 29 ", " male ", " Mombasa ", "  Bamburi"]
    outcome = registration.start_registration(db, PHONE, messy)
    assert outcome.error is None
    assert outcome.user.name == "Jamal Jalang'o"
    assert outcome.user.age == 29
    assert outcome.user.gender == "Male"


@pytest.mark.parametrize(
    ("typed", "saved"),
    [
        ("male", "Male"),
        ("MALE", "Male"),
        ("Male", "Male"),
        ("female", "Female"),
        ("FEMALE", "Female"),
        ("Female", "Female"),
    ],
)
def test_gender_is_accepted_in_any_case_and_saved_properly(db, typed, saved):
    outcome = registration.start_registration(db, PHONE, fields_with(2, typed))
    assert outcome.error is None
    assert outcome.user.gender == saved


@pytest.mark.parametrize("age", [18, 99])
def test_the_age_limits_themselves_are_allowed(db, age):
    outcome = registration.start_registration(db, PHONE, fields_with(1, str(age)))
    assert outcome.error is None
    assert outcome.user.age == age


@pytest.mark.parametrize("age", ["17", "100", "0", "9" * 5000])
def test_age_outside_the_limits_is_refused(db, age):
    outcome = registration.start_registration(db, PHONE, fields_with(1, age))
    assert outcome.error == StartError.AGE_OUT_OF_RANGE


@pytest.mark.parametrize("age", ["abc", "", "29.5", "-5", "\u00b2", "twenty"])
def test_age_that_is_not_a_number_is_refused(db, age):
    outcome = registration.start_registration(db, PHONE, fields_with(1, age))
    assert outcome.error == StartError.AGE_NOT_A_NUMBER


@pytest.mark.parametrize("gender", ["", "M", "other", "Mal"])
def test_unknown_gender_is_refused(db, gender):
    outcome = registration.start_registration(db, PHONE, fields_with(2, gender))
    assert outcome.error == StartError.INVALID_GENDER


@pytest.mark.parametrize("bad", [[], FIELDS[:4], FIELDS + ["extra"]])
def test_wrong_number_of_fields_is_refused(db, bad):
    outcome = registration.start_registration(db, PHONE, bad)
    assert outcome.error == StartError.WRONG_FIELD_COUNT


@pytest.mark.parametrize(("index", "value"), [(0, ""), (3, ""), (4, "   ")])
def test_empty_name_county_or_town_is_refused(db, index, value):
    outcome = registration.start_registration(db, PHONE, fields_with(index, value))
    assert outcome.error == StartError.MISSING_FIELD


@pytest.mark.parametrize(("index", "value"), [(0, "a" * 101), (3, "a" * 51), (4, "a" * 51)])
def test_name_county_or_town_over_the_limit_is_refused(db, index, value):
    outcome = registration.start_registration(db, PHONE, fields_with(index, value))
    assert outcome.error == StartError.FIELD_TOO_LONG


@pytest.mark.parametrize(("index", "value"), [(0, "a" * 100), (3, "a" * 50), (4, "a" * 50)])
def test_name_county_or_town_at_the_limit_is_allowed(db, index, value):
    outcome = registration.start_registration(db, PHONE, fields_with(index, value))
    assert outcome.error is None


def test_a_refused_registration_saves_nothing(db):
    registration.start_registration(db, PHONE, fields_with(1, "17"))
    assert user_repo.get_by_phone(db, PHONE) is None
    assert count_users(db) == 0


def test_second_registration_returns_the_existing_user_unchanged(db):
    first = registration.start_registration(db, PHONE, FIELDS).user
    second = registration.start_registration(db, PHONE, fields_with(0, "Someone Else"))
    assert second.error == StartError.ALREADY_REGISTERED
    assert second.user.id == first.id
    assert second.user.name == "Jamal Jalang'o"
    assert count_users(db) == 1


def test_already_registered_is_reported_before_validation(db):
    registration.start_registration(db, PHONE, FIELDS)
    outcome = registration.start_registration(db, PHONE, [])
    assert outcome.error == StartError.ALREADY_REGISTERED


def test_a_race_for_the_same_phone_is_reported_as_already_registered(db, monkeypatch):
    existing = user_repo.create(
        db,
        phone=PHONE,
        name="Jamal Jalang'o",
        age=29,
        gender="Male",
        county="Mombasa",
        town="Bamburi",
    )
    real_lookup = user_repo.get_by_phone
    calls = []

    def lookup_that_misses_first(session, phone):
        calls.append(phone)
        if len(calls) == 1:
            return None
        return real_lookup(session, phone)

    monkeypatch.setattr(user_repo, "get_by_phone", lookup_that_misses_first)

    outcome = registration.start_registration(db, PHONE, FIELDS)

    assert outcome.error == StartError.ALREADY_REGISTERED
    assert outcome.user.id == existing.id
    assert count_users(db) == 1


def test_length_limits_match_the_database_columns():
    columns = User.__table__.c
    assert registration.NAME_MAX == columns.name.type.length
    assert registration.COUNTY_MAX == columns.county.type.length
    assert registration.TOWN_MAX == columns.town.type.length


def test_phone_must_be_in_stored_format():
    with pytest.raises(ValueError):
        registration.start_registration(None, "0712345678", FIELDS)