import re

_SEPARATORS = re.compile(r"[\s\-]")
_LOCAL = re.compile(r"0([71][0-9]{8})")
_INTERNATIONAL = re.compile(r"\+?254([71][0-9]{8})")
_BARE = re.compile(r"([71][0-9]{8})")


def normalize_phone(raw: str) -> str | None:
    cleaned = _SEPARATORS.sub("", raw)
    found = (
        _LOCAL.fullmatch(cleaned)
        or _INTERNATIONAL.fullmatch(cleaned)
        or _BARE.fullmatch(cleaned)
    )
    if found is None:
        return None
    return "254" + found.group(1)


def display_phone(stored: str) -> str:
    if len(stored) == 12 and stored.startswith("254"):
        return "0" + stored[3:]
    return stored