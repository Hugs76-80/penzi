import pytest

from app.config import settings
from app.core import templates
from app.core.parser import parse
from app.handlers import start
from app.repositories import user_repo
from app.schemas.sms import Reply
from app.services.registration import MAX_AGE, MIN_AGE

PHONE = "254712345678"
CODE = settings.shortcode
GOOD = ["Jamal Jalang'o", "29", "Male", "Mombasa", "Bamburi"]


def register(db):
    return user_repo.create(
        db,
        phone=PHONE,
        name="Jamal Jalang'o",
        age=29,
        gender="Male",
        county="Mombasa",
        town="Bamburi",
    )


def test_a_valid_start_registers_the_user_and_replies_once(db):
    replies = start.handle(db, PHONE, GOOD)
    assert replies == [
        Reply(to=PHONE, text=templates.profile_created("Jamal Jalang'o", CODE))
    ]
    assert replies[0].text.startswith(
        "Your profile has been created successfully Jamal."
    )
    user = user_repo.get_by_phone(db, PHONE)
    assert user is not None
    assert user.registration_stage == "STARTED"


def test_a_raw_message_through_the_parser_registers_correctly(db):
    parsed = parse("START# Jamal Jalang'o #29#male#Mombasa#Bamburi")
    replies = start.handle(db, PHONE, parsed.args)
    assert replies[0].text.startswith("Your profile has been created")
    user = user_repo.get_by_phone(db, PHONE)
    assert user.name == "Jamal Jalang'o"
    assert user.gender == "Male"


def test_wrong_field_count_shows_the_format(db):
    replies = start.handle(db, PHONE, ["Jamal", "29"])
    assert replies[0].text == templates.start_format_error(CODE)


def test_empty_name_shows_the_format(db):
    replies = start.handle(db, PHONE, ["", "29", "Male", "Mombasa", "Bamburi"])
    assert replies[0].text == templates.start_format_error(CODE)


@pytest.mark.parametrize("age", ["abc", "17"])
def test_bad_age_states_the_limits(db, age):
    replies = start.handle(db, PHONE, ["Jamal", age, "Male", "Mombasa", "Bamburi"])
    assert replies[0].text == templates.invalid_age(MIN_AGE, MAX_AGE)


def test_bad_gender_names_the_choices(db):
    replies = start.handle(db, PHONE, ["Jamal", "29", "other", "Mombasa", "Bamburi"])
    assert replies[0].text == templates.invalid_gender()


def test_text_that_is_too_long_is_refused(db):
    replies = start.handle(db, PHONE, ["a" * 101, "29", "Male", "Mombasa", "Bamburi"])
    assert replies[0].text == templates.start_text_too_long()


def test_a_refused_message_saves_nobody(db):
    start.handle(db, PHONE, ["Jamal", "17", "Male", "Mombasa", "Bamburi"])
    assert user_repo.get_by_phone(db, PHONE) is None


def test_already_registered_at_started_points_to_details(db):
    register(db)
    replies = start.handle(db, PHONE, GOOD)
    assert replies[0].text == templates.already_registered_started(
        "Jamal Jalang'o", CODE
    )


def test_already_registered_with_details_points_to_myself(db):
    user = register(db)
    user_repo.save_details(db, user, "graduate", "accountant", "divorced", "muslim", "somali")
    replies = start.handle(db, PHONE, GOOD)
    assert replies[0].text == templates.already_registered_details_done(
        "Jamal Jalang'o", CODE
    )

def test_already_registered_and_complete_points_to_matching(db):
    user = register(db)
    user_repo.save_description(db, user, "tall, dark and handsome")
    replies = start.handle(db, PHONE, GOOD)
    assert replies[0].text == templates.already_registered_complete(
        "Jamal Jalang'o", CODE
    )


def test_a_repeat_start_never_changes_the_saved_profile(db):
    register(db)
    start.handle(db, PHONE, ["Someone Else", "40", "Female", "Nairobi", "Kasarani"])
    user = user_repo.get_by_phone(db, PHONE)
    assert user.name == "Jamal Jalang'o"
    assert user.age == 29
    assert user.gender == "Male"