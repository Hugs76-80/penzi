from app.config import settings
from app.core import templates
from app.core.parser import parse
from app.handlers import details, start
from app.repositories import user_repo
from app.schemas.sms import Reply

PHONE = "254712345678"
CODE = settings.shortcode
GOOD = ["diploma", "driver", "single", "christian", "mijikenda"]


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


def test_valid_details_ask_for_the_description(db):
    register(db)
    replies = details.handle(db, PHONE, GOOD)
    assert replies == [Reply(to=PHONE, text=templates.ask_for_description(CODE))]
    assert replies[0].text.startswith("This is the last stage of registration.")
    user = user_repo.get_by_phone(db, PHONE)
    assert user.registration_stage == "DETAILS_DONE"
    assert user.education == "Diploma"


def test_a_raw_message_through_the_parser_saves_correctly(db):
    register(db)
    parsed = parse("DETAILS# graduate #accountant#divorced#muslim#somali")
    replies = details.handle(db, PHONE, parsed.args)
    assert replies[0].text == templates.ask_for_description(CODE)
    user = user_repo.get_by_phone(db, PHONE)
    assert user.education == "Graduate"
    assert user.marital_status == "divorced"


def test_an_unregistered_sender_gets_the_welcome_message(db):
    replies = details.handle(db, PHONE, GOOD)
    assert replies == [Reply(to=PHONE, text=templates.welcome(CODE))]
    assert user_repo.get_by_phone(db, PHONE) is None


def test_wrong_field_count_shows_the_format(db):
    register(db)
    replies = details.handle(db, PHONE, ["diploma", "driver"])
    assert replies[0].text == templates.details_format_error(CODE)


def test_an_empty_field_shows_the_format(db):
    register(db)
    replies = details.handle(db, PHONE, ["diploma", "", "single", "christian", "luo"])
    assert replies[0].text == templates.details_format_error(CODE)


def test_a_value_that_is_too_long_is_refused(db):
    register(db)
    replies = details.handle(
        db, PHONE, ["a" * 51, "driver", "single", "christian", "luo"]
    )
    assert replies[0].text == templates.details_text_too_long()


def test_a_refused_message_saves_nothing(db):
    register(db)
    details.handle(db, PHONE, ["diploma", "driver", "single", "christian", ""])
    user = user_repo.get_by_phone(db, PHONE)
    assert user.education is None
    assert user.registration_stage == "STARTED"


def test_sending_details_twice_overwrites_and_asks_for_the_description_again(db):
    register(db)
    details.handle(db, PHONE, GOOD)
    replies = details.handle(
        db, PHONE, ["graduate", "accountant", "divorced", "muslim", "somali"]
    )
    assert replies[0].text == templates.ask_for_description(CODE)
    user = user_repo.get_by_phone(db, PHONE)
    assert user.education == "Graduate"
    assert user.registration_stage == "DETAILS_DONE"


def test_a_completed_user_is_told_their_details_were_updated(db):
    user = register(db)
    user_repo.save_description(db, user, "tall, dark and handsome")
    replies = details.handle(db, PHONE, GOOD)
    assert replies[0].text == templates.details_updated(CODE)
    assert user_repo.get_by_phone(db, PHONE).registration_stage == "COMPLETE"


def test_start_then_details_through_the_handlers(db):
    start.handle(db, PHONE, ["Jamal Jalang'o", "29", "Male", "Mombasa", "Bamburi"])
    replies = details.handle(
        db, PHONE, ["graduate", "accountant", "divorced", "muslim", "somali"]
    )
    assert replies[0].text == templates.ask_for_description(CODE)
    user = user_repo.get_by_phone(db, PHONE)
    assert user.name == "Jamal Jalang'o"
    assert user.education == "Graduate"
    assert user.registration_stage == "DETAILS_DONE"