import pytest
from sqlalchemy import func, select

from app.models.user import User
from app.repositories import user_repo
from app.services import registration
from app.services.registration import DetailsError

PHONE = "254712345678"
FIELDS = ["diploma", "driver", "single", "christian", "mijikenda"]


def register(db, phone=PHONE):
    return user_repo.create(
        db,
        phone=phone,
        name="Jamal Jalang'o",
        age=29,
        gender="Male",
        county="Mombasa",
        town="Bamburi",
    )


def fields_with(index, value):
    changed = list(FIELDS)
    changed[index] = value
    return changed


def count_users(db):
    return db.scalar(select(func.count()).select_from(User))


def test_valid_details_are_saved_and_the_stage_advances(db):
    register(db)
    outcome = registration.save_user_details(db, PHONE, FIELDS)
    assert outcome.error is None
    user = outcome.user
    assert user.education == "Diploma"
    assert user.profession == "Driver"
    assert user.marital_status == "single"
    assert user.religion == "Christian"
    assert user.ethnicity == "Mijikenda"
    assert user.registration_stage == "DETAILS_DONE"


def test_the_pdf_example_is_stored_the_way_the_pdf_shows_it(db):
    register(db)
    fields = ["graduate", "accountant", "divorced", "muslim", "somali"]
    user = registration.save_user_details(db, PHONE, fields).user
    assert user.education == "Graduate"
    assert user.profession == "Accountant"
    assert user.marital_status == "divorced"
    assert user.religion == "Muslim"
    assert user.ethnicity == "Somali"


def test_extra_spaces_are_cleaned(db):
    register(db)
    messy = ["  senior   diploma ", " driver ", " single", "christian ", "  mijikenda"]
    user = registration.save_user_details(db, PHONE, messy).user
    assert user.education == "Senior diploma"
    assert user.profession == "Driver"


def test_capitals_inside_a_value_are_kept_and_marital_status_is_lowercased(db):
    register(db)
    fields = ["BSc Computer Science", "ICT Officer", "SINGLE", "Seventh-day Adventist", "Luo"]
    user = registration.save_user_details(db, PHONE, fields).user
    assert user.education == "BSc Computer Science"
    assert user.profession == "ICT Officer"
    assert user.marital_status == "single"
    assert user.religion == "Seventh-day Adventist"


def test_an_unregistered_sender_is_told_to_register(db):
    outcome = registration.save_user_details(db, PHONE, FIELDS)
    assert outcome.error == DetailsError.NOT_REGISTERED
    assert outcome.user is None
    assert count_users(db) == 0


@pytest.mark.parametrize("bad", [[], FIELDS[:4], FIELDS + ["extra"]])
def test_wrong_number_of_fields_is_refused(db, bad):
    register(db)
    outcome = registration.save_user_details(db, PHONE, bad)
    assert outcome.error == DetailsError.WRONG_FIELD_COUNT


@pytest.mark.parametrize(
    ("index", "value"), [(0, ""), (1, "   "), (2, ""), (3, "   "), (4, "")]
)
def test_an_empty_field_is_refused(db, index, value):
    register(db)
    outcome = registration.save_user_details(db, PHONE, fields_with(index, value))
    assert outcome.error == DetailsError.MISSING_FIELD


@pytest.mark.parametrize(
    ("index", "limit"), [(0, 50), (1, 50), (2, 30), (3, 30), (4, 50)]
)
def test_a_value_over_its_column_size_is_refused(db, index, limit):
    register(db)
    outcome = registration.save_user_details(
        db, PHONE, fields_with(index, "a" * (limit + 1))
    )
    assert outcome.error == DetailsError.FIELD_TOO_LONG


@pytest.mark.parametrize(
    ("index", "limit"), [(0, 50), (1, 50), (2, 30), (3, 30), (4, 50)]
)
def test_a_value_exactly_at_its_column_size_is_allowed(db, index, limit):
    register(db)
    outcome = registration.save_user_details(db, PHONE, fields_with(index, "a" * limit))
    assert outcome.error is None


def test_a_refused_message_changes_nothing(db):
    register(db)
    registration.save_user_details(db, PHONE, fields_with(4, ""))
    user = user_repo.get_by_phone(db, PHONE)
    assert user.education is None
    assert user.registration_stage == "STARTED"


def test_sending_details_again_overwrites_the_old_values(db):
    register(db)
    registration.save_user_details(db, PHONE, FIELDS)
    again = ["graduate", "accountant", "divorced", "muslim", "somali"]
    user = registration.save_user_details(db, PHONE, again).user
    assert user.education == "Graduate"
    assert user.marital_status == "divorced"
    assert user.registration_stage == "DETAILS_DONE"


def test_details_after_completion_keep_the_stage_complete(db):
    user = register(db)
    user_repo.save_description(db, user, "tall, dark and handsome")
    outcome = registration.save_user_details(db, PHONE, FIELDS)
    assert outcome.user.registration_stage == "COMPLETE"
    assert outcome.user.education == "Diploma"


def test_phone_must_be_in_stored_format():
    with pytest.raises(ValueError):
        registration.save_user_details(None, "0712345678", FIELDS)


def test_length_limits_match_the_database_columns():
    columns = User.__table__.c
    assert registration.EDUCATION_MAX == columns.education.type.length
    assert registration.PROFESSION_MAX == columns.profession.type.length
    assert registration.MARITAL_STATUS_MAX == columns.marital_status.type.length
    assert registration.RELIGION_MAX == columns.religion.type.length
    assert registration.ETHNICITY_MAX == columns.ethnicity.type.length