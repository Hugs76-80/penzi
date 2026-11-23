import pytest

from app.core.parser import Command, parse


@pytest.mark.parametrize(
    "text",
    [
        "start#Jamal Jalang'o#29#Male#Mombasa#Bamburi",
        "START#Jamal Jalang'o#29#Male#Mombasa#Bamburi",
        "  Start#Jamal Jalang'o#29#Male#Mombasa#Bamburi  ",
    ],
)
def test_start_is_recognised_in_any_case(text):
    result = parse(text)
    assert result.command == Command.START
    assert result.args == ["Jamal Jalang'o", "29", "Male", "Mombasa", "Bamburi"]


def test_start_trims_spaces_around_fields():
    result = parse("start# Jamal #29 #Male# Mombasa #Bamburi")
    assert result.args == ["Jamal", "29", "Male", "Mombasa", "Bamburi"]


def test_start_with_missing_fields_still_parses():
    result = parse("start#Jamal#29")
    assert result.command == Command.START
    assert result.args == ["Jamal", "29"]


def test_details_splits_fields():
    result = parse("details#graduate#accountant#divorced#muslim#somali")
    assert result.command == Command.DETAILS
    assert result.args == ["graduate", "accountant", "divorced", "muslim", "somali"]


@pytest.mark.parametrize("text", ["match#26-30#Nairobi", "MATCH#26-30#Nairobi"])
def test_match_splits_range_and_place(text):
    result = parse(text)
    assert result.command == Command.MATCH
    assert result.args == ["26-30", "Nairobi"]


def test_myself_takes_the_free_text():
    result = parse("MYSELF tall, dark and handsome")
    assert result.command == Command.MYSELF
    assert result.args == ["tall, dark and handsome"]


def test_myself_is_case_insensitive():
    result = parse("myself chocolate, lovely")
    assert result.command == Command.MYSELF
    assert result.args == ["chocolate, lovely"]


def test_myself_keeps_hash_characters_in_the_text():
    result = parse("MYSELF I love #music")
    assert result.command == Command.MYSELF
    assert result.args == ["I love #music"]


def test_myself_without_text_gives_an_empty_argument():
    result = parse("MYSELF")
    assert result.command == Command.MYSELF
    assert result.args == [""]


def test_myself_needs_a_word_boundary():
    assert parse("myselfie").command == Command.UNKNOWN


def test_describe_takes_the_number_as_typed():
    result = parse("DESCRIBE 0702556677")
    assert result.command == Command.DESCRIBE
    assert result.args == ["0702556677"]


def test_describe_wins_over_phone_lookup():
    assert parse("describe 0702556677").command == Command.DESCRIBE


def test_describe_without_a_number_gives_an_empty_argument():
    result = parse("DESCRIBE")
    assert result.command == Command.DESCRIBE
    assert result.args == [""]


@pytest.mark.parametrize("text", ["NEXT", "next", "  Next  "])
def test_next_is_recognised(text):
    assert parse(text).command == Command.NEXT


@pytest.mark.parametrize("text", ["YES", "yes", " Yes "])
def test_yes_is_recognised(text):
    assert parse(text).command == Command.YES


@pytest.mark.parametrize("text", ["yes please", "yesterday", "next page"])
def test_yes_and_next_must_be_the_whole_message(text):
    assert parse(text).command == Command.UNKNOWN


@pytest.mark.parametrize(
    "text",
    [
        "0702556677",
        "+254702556677",
        "254702556677",
        "702556677",
        "0702 556 677",
        "+254 702 556 677",
    ],
)
def test_phone_number_becomes_a_lookup(text):
    result = parse(text)
    assert result.command == Command.LOOKUP
    assert result.args == ["254702556677"]


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "hello",
        "start",
        "7355655",
        "812345678",
        "hello 702556677",
        "hello 0702556677",
    ],
)
def test_everything_else_is_unknown(text):
    result = parse(text)
    assert result.command == Command.UNKNOWN
    assert result.args == []