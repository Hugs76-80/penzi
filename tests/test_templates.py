import pytest

from app.core import templates as t
from app.core.templates import MatchLine, Profile

CODE = "22141"


@pytest.mark.parametrize(
    ("full_name", "expected"),
    [
        ("Jamal Jalang'o", "Jamal"),
        ("  Maria  ", "Maria"),
        ("Aisha", "Aisha"),
        ("", ""),
    ],
)
def test_first_name(full_name, expected):
    assert t.first_name(full_name) == expected


@pytest.mark.parametrize(
    ("gender", "person"),
    [("male", "man"), ("MALE", "man"), ("Female", "lady"), ("FEMALE", "lady")],
)
def test_words_for_ignores_case(gender, person):
    assert t.words_for(gender).person == person


def test_welcome_matches_the_pdf():
    assert t.welcome(CODE) == (
        "Welcome to our dating service with 6000 potential dating partners!\n"
        "To register SMS start#name#age#gender#county#town to 22141.\n"
        "E.g., start#John Doe#26#Male#Nakuru#Naivasha"
    )


def test_profile_created_matches_the_pdf():
    assert t.profile_created("Jamal Jalang'o", CODE) == (
        "Your profile has been created successfully Jamal.\n"
        "SMS details#levelOfEducation#profession#maritalStatus#religion"
        "#ethnicity to 22141.\n"
        "E.g. details#diploma#driver#single#christian#mijikenda"
    )


def test_registered_with_initial_details_matches_the_pdf():
    assert t.registered_with_initial_details(CODE) == (
        "You were registered for dating with your initial details.\n"
        "To search for a MPENZI, SMS match#age#town to 22141 "
        "and meet the person of your dreams.\n"
        "E.g., match#23-25#Nairobi"
    )


def test_ask_for_description_matches_the_pdf():
    assert t.ask_for_description(CODE) == (
        "This is the last stage of registration.\n"
        "SMS a brief description of yourself to 22141 starting with the word MYSELF.\n"
        "E.g., MYSELF chocolate, lovely, sexy etc."
    )


def test_registration_complete_matches_the_pdf():
    assert t.registration_complete(CODE) == (
        "You are now registered for dating.\n"
        "To search for a MPENZI, SMS match#age#town to 22141 "
        "and meet the person of your dreams.\n"
        "E.g., match#23-25#Kisumu"
    )


def test_shortcode_comes_from_the_argument():
    text = t.welcome("99999")
    assert "to 99999." in text
    assert "22141" not in text


def test_match_count_for_a_man_searching():
    assert t.match_count(32, 3, "Female", CODE) == (
        "We have 32 ladies who match your choice! "
        "We will send you details of 3 of them shortly.\n"
        "To get more details about a lady, SMS her number e.g., 0722010203 to 22141"
    )


def test_match_count_for_a_woman_searching():
    assert t.match_count(12, 3, "Male", CODE) == (
        "We have 12 men who match your choice! "
        "We will send you details of 3 of them shortly.\n"
        "To get more details about a man, SMS his number e.g., 0722010203 to 22141"
    )


def test_match_count_with_a_single_match():
    assert t.match_count(1, 1, "Female", CODE) == (
        "We have 1 lady who matches your choice! "
        "We will send you the details shortly.\n"
        "To get more details about a lady, SMS her number e.g., 0722010203 to 22141"
    )


def test_match_page_with_more_to_come():
    lines = [
        MatchLine("Lina Moraa", 29, "254722010203"),
        MatchLine("Dorine Gakii", 26, "254701223344"),
        MatchLine("Aisha Bahati", 27, "254700112233"),
    ]
    assert t.match_page(lines, 29, "Female", CODE) == (
        "Lina Moraa aged 29, 0722010203.\n"
        "Dorine Gakii aged 26, 0701223344.\n"
        "Aisha Bahati aged 27, 0700112233.\n"
        "Send NEXT to 22141 to receive details of the remaining 29 ladies"
    )


def test_match_page_on_the_last_page():
    lines = [
        MatchLine("Wanjiru Kamau", 27, "254711222333"),
        MatchLine("Njeri Wambui", 29, "254722333444"),
    ]
    assert t.match_page(lines, 0, "Female", CODE) == (
        "Wanjiru Kamau aged 27, 0711222333.\n"
        "Njeri Wambui aged 29, 0722333444.\n"
        "That's all the matches for this search. "
        "SMS match#age#town to 22141 to search again."
    )


def test_match_page_with_one_remaining_uses_the_singular():
    lines = [MatchLine("Wanjiru Kamau", 27, "254711222333")]
    text = t.match_page(lines, 1, "Female", CODE)
    assert text.endswith("the remaining 1 lady")


def test_profile_details_matches_the_pdf():
    profile = Profile(
        name="Maria Mwende",
        age=28,
        county="Nairobi",
        town="Kasarani",
        phone="254702556677",
        education="Graduate",
        profession="Nurse",
        marital_status="single",
        religion="Christian",
        ethnicity="Kamba",
    )
    assert t.profile_details(profile) == (
        "Maria Mwende aged 28, Nairobi County, Kasarani town, Graduate, Nurse, "
        "single, Christian, Kamba. "
        "Send DESCRIBE 0702556677 to get more details about Maria."
    )


def test_profile_details_leaves_out_missing_fields():
    profile = Profile(
        name="Maria Mwende",
        age=28,
        county="Nairobi",
        town="Kasarani",
        phone="254702556677",
    )
    text = t.profile_details(profile)
    assert text == (
        "Maria Mwende aged 28, Nairobi County, Kasarani town. "
        "Send DESCRIBE 0702556677 to get more details about Maria."
    )
    assert "None" not in text


def test_interest_notice_for_a_male_requester():
    assert t.interest_notice("Maria Mwende", "Jamal Jalang'o", 29, "Mombasa", "Male", CODE) == (
        "Hi Maria, a man called Jamal is interested in you "
        "and requested your details.\n"
        "He is aged 29 based in Mombasa.\n"
        "Do you want to know more about him? Send YES to 22141"
    )


def test_interest_notice_for_a_female_requester():
    assert t.interest_notice("Peter Otieno", "Aisha Bahati", 27, "Kisumu", "Female", CODE) == (
        "Hi Peter, a lady called Aisha is interested in you "
        "and requested your details.\n"
        "She is aged 27 based in Kisumu.\n"
        "Do you want to know more about her? Send YES to 22141"
    )


def test_description_reply_for_a_woman():
    text = "Diligent, loving, dedicated and will make you tick"
    assert t.description_reply("Maria Mwende", "Female", text) == (
        "Maria describes herself as Diligent, loving, dedicated "
        "and will make you tick"
    )


def test_description_reply_for_a_man():
    assert t.description_reply("Jamal Jalang'o", "Male", "tall and dark") == (
        "Jamal describes himself as tall and dark"
    )


def test_unknown_command_explains_how_to_start():
    assert t.unknown_command(CODE) == (
        "Sorry, we did not understand that.\n"
        "To register SMS start#name#age#gender#county#town to 22141.\n"
        "To search SMS match#age#town to 22141."
    )