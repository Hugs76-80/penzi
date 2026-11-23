import re
from dataclasses import dataclass, field
from enum import StrEnum

from app.utils.phone import normalize_phone


class Command(StrEnum):
    START = "start"
    DETAILS = "details"
    MATCH = "match"
    MYSELF = "myself"
    DESCRIBE = "describe"
    NEXT = "next"
    YES = "yes"
    LOOKUP = "lookup"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ParsedCommand:
    command: Command
    args: list[str] = field(default_factory=list)


_HASH_COMMANDS = {
    "start#": Command.START,
    "details#": Command.DETAILS,
    "match#": Command.MATCH,
}

_MYSELF = re.compile(r"myself\b(.*)", re.IGNORECASE | re.DOTALL)
_DESCRIBE = re.compile(r"describe\b(.*)", re.IGNORECASE | re.DOTALL)


def parse(text: str) -> ParsedCommand:
    cleaned = text.strip()
    lowered = cleaned.lower()

    for prefix, command in _HASH_COMMANDS.items():
        if lowered.startswith(prefix):
            fields = [part.strip() for part in cleaned.split("#")[1:]]
            return ParsedCommand(command, fields)

    found = _MYSELF.fullmatch(cleaned)
    if found:
        return ParsedCommand(Command.MYSELF, [found.group(1).strip()])

    found = _DESCRIBE.fullmatch(cleaned)
    if found:
        return ParsedCommand(Command.DESCRIBE, [found.group(1).strip()])

    if lowered == "next":
        return ParsedCommand(Command.NEXT)
    if lowered == "yes":
        return ParsedCommand(Command.YES)

    phone = normalize_phone(cleaned)
    if phone is not None:
        return ParsedCommand(Command.LOOKUP, [phone])

    return ParsedCommand(Command.UNKNOWN)