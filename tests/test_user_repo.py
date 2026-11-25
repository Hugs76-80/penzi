import pytest
from sqlalchemy.exc import IntegrityError

from app.repositories import user_repo

PHONE = "254712345678"

DETAILS = {
    "education": "graduate",
    "profession": "accountant",
    "marital_status": "divorced",
    "religion": "muslim",
    "ethnicity": "somali",
}


def make_user(db, phone=PHONE):
    return user_repo.create(
        db,
        phone=phone,
        name="Jamal Jalang'o",
        age=29,
        gender="Male",
        county="Mombasa",
        town="Bamburi",
    )


def test_get_by_phone_returns_none_when_missing(db):
    assert user_repo.get_by_phone(db, PHONE) is None


def test_create_saves_a_user_in_the_started_stage(db):
    user = make_user(db)
    assert user.id is not None
    assert user.phone == PHONE
    assert user.name == "Jamal Jalang'o"
    assert user.age == 29
    assert user.gender == "Male"
    assert user.county == "Mombasa"
    assert user.town == "Bamburi"
    assert user.registration_stage == "STARTED"
    assert user.education is None
    assert user.description is None


def test_get_by_phone_finds_the_user(db):
    created = make_user(db)
    found = user_repo.get_by_phone(db, PHONE)
    assert found is not None
    assert found.id == created.id


def test_get_by_phone_only_finds_the_matching_number(db):
    make_user(db)
    assert user_repo.get_by_phone(db, "254722000000") is None


def test_created_at_is_filled_in_by_the_database(db):
    assert make_user(db).created_at is not None


def test_duplicate_phone_is_refused_by_the_database(db):
    make_user(db)
    with pytest.raises(IntegrityError):
        make_user(db)


@pytest.mark.parametrize(
    "phone", ["0712345678", "+254712345678", "712345678", "254 712 345 678", ""]
)
def test_phone_must_be_in_stored_format(db, phone):
    with pytest.raises(ValueError):
        user_repo.get_by_phone(db, phone)
    with pytest.raises(ValueError):
        make_user(db, phone=phone)


def test_save_details_fills_the_columns_and_advances_the_stage(db):
    user = make_user(db)
    user_repo.save_details(db, user, **DETAILS)
    assert user.education == "graduate"
    assert user.profession == "accountant"
    assert user.marital_status == "divorced"
    assert user.religion == "muslim"
    assert user.ethnicity == "somali"
    assert user.registration_stage == "DETAILS_DONE"


def test_save_description_completes_registration(db):
    user = make_user(db)
    user_repo.save_details(db, user, **DETAILS)
    user_repo.save_description(db, user, "tall, dark and handsome")
    assert user.description == "tall, dark and handsome"
    assert user.registration_stage == "COMPLETE"


def test_save_description_without_details_still_completes(db):
    user = make_user(db)
    user_repo.save_description(db, user, "chocolate, lovely")
    assert user.registration_stage == "COMPLETE"
    assert user.education is None


def test_stage_never_moves_backwards(db):
    user = make_user(db)
    user_repo.save_description(db, user, "tall")
    user_repo.save_details(db, user, **DETAILS)
    assert user.registration_stage == "COMPLETE"
    assert user.education == "graduate"


def test_changes_are_really_written_to_the_database(db):
    user = make_user(db)
    user_repo.save_description(db, user, "tall")
    db.expire_all()
    found = user_repo.get_by_phone(db, PHONE)
    assert found is not None
    assert found.description == "tall"