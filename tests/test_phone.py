import pytest

from app.utils.phone import display_phone, normalize_phone


@pytest.mark.parametrize(
    "raw",
    [
        "0702556677",
        "+254702556677",
        "254702556677",
        "702556677",
        "0702 556 677",
        "0702-556-677",
        "+254 702 556 677",
        "  0702556677  ",
    ],
)
def test_normalize_accepts_valid_formats(raw):
    assert normalize_phone(raw) == "254702556677"


def test_normalize_accepts_01_prefix():
    assert normalize_phone("0112345678") == "254112345678"


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "7355655",
        "070255667",
        "07025566777",
        "0802556677",
        "812345678",
        "hello 0702556677",
        "+255702556677",
        "abc",
    ],
)
def test_normalize_rejects_invalid(raw):
    assert normalize_phone(raw) is None


def test_display_converts_to_local_format():
    assert display_phone("254702556677") == "0702556677"


def test_display_leaves_unexpected_values_alone():
    assert display_phone("12345") == "12345"


def test_display_and_normalize_round_trip():
    assert normalize_phone(display_phone("254702556677")) == "254702556677"