from dataclasses import dataclass

from app.utils.phone import display_phone


@dataclass(frozen=True)
class Words:
    person: str
    plural: str
    subject_pronoun: str
    object_pronoun: str
    possessive: str
    reflexive: str


_MALE = Words("man", "men", "He", "him", "his", "himself")
_FEMALE = Words("lady", "ladies", "She", "her", "her", "herself")


def words_for(gender: str) -> Words:
    return _FEMALE if gender.strip().lower() == "female" else _MALE


def first_name(full_name: str) -> str:
    parts = full_name.split()
    return parts[0] if parts else ""


@dataclass(frozen=True)
class Profile:
    name: str
    age: int
    county: str
    town: str
    phone: str
    education: str | None = None
    profession: str | None = None
    marital_status: str | None = None
    religion: str | None = None
    ethnicity: str | None = None


@dataclass(frozen=True)
class MatchLine:
    name: str
    age: int
    phone: str


def _search_hint(code: str, example_town: str) -> str:
    return (
        f"To search for a MPENZI, SMS match#age#town to {code} "
        "and meet the person of your dreams.\n"
        f"E.g., match#23-25#{example_town}"
    )


def welcome(code: str) -> str:
    return (
        "Welcome to our dating service with 6000 potential dating partners!\n"
        f"To register SMS start#name#age#gender#county#town to {code}.\n"
        "E.g., start#John Doe#26#Male#Nakuru#Naivasha"
    )


def profile_created(name: str, code: str) -> str:
    return (
        f"Your profile has been created successfully {first_name(name)}.\n"
        "SMS details#levelOfEducation#profession#maritalStatus#religion"
        f"#ethnicity to {code}.\n"
        "E.g. details#diploma#driver#single#christian#mijikenda"
    )


def registered_with_initial_details(code: str) -> str:
    return (
        "You were registered for dating with your initial details.\n"
        + _search_hint(code, "Nairobi")
    )


def ask_for_description(code: str) -> str:
    return (
        "This is the last stage of registration.\n"
        "SMS a brief description of yourself to "
        f"{code} starting with the word MYSELF.\n"
        "E.g., MYSELF chocolate, lovely, sexy etc."
    )


def registration_complete(code: str) -> str:
    return "You are now registered for dating.\n" + _search_hint(code, "Kisumu")


def match_count(total: int, shown: int, found_gender: str, code: str) -> str:
    w = words_for(found_gender)
    if total == 1:
        head = (
            f"We have 1 {w.person} who matches your choice! "
            "We will send you the details shortly."
        )
    else:
        head = (
            f"We have {total} {w.plural} who match your choice! "
            f"We will send you details of {shown} of them shortly."
        )
    return (
        f"{head}\n"
        f"To get more details about a {w.person}, "
        f"SMS {w.possessive} number e.g., 0722010203 to {code}"
    )


def match_page(
    lines: list[MatchLine], remaining: int, found_gender: str, code: str
) -> str:
    w = words_for(found_gender)
    rows = [f"{x.name} aged {x.age}, {display_phone(x.phone)}." for x in lines]
    if remaining > 0:
        noun = w.person if remaining == 1 else w.plural
        rows.append(
            f"Send NEXT to {code} to receive details of the remaining "
            f"{remaining} {noun}"
        )
    else:
        rows.append(
            "That's all the matches for this search. "
            f"SMS match#age#town to {code} to search again."
        )
    return "\n".join(rows)


def profile_details(p: Profile) -> str:
    parts = [f"{p.name} aged {p.age}", f"{p.county} County", f"{p.town} town"]
    optional = [p.education, p.profession, p.marital_status, p.religion, p.ethnicity]
    parts += [value for value in optional if value]
    return (
        f"{', '.join(parts)}. "
        f"Send DESCRIBE {display_phone(p.phone)} "
        f"to get more details about {first_name(p.name)}."
    )


def interest_notice(
    target_name: str,
    requester_name: str,
    requester_age: int,
    requester_county: str,
    requester_gender: str,
    code: str,
) -> str:
    w = words_for(requester_gender)
    return (
        f"Hi {first_name(target_name)}, a {w.person} called "
        f"{first_name(requester_name)} is interested in you "
        "and requested your details.\n"
        f"{w.subject_pronoun} is aged {requester_age} based in {requester_county}.\n"
        f"Do you want to know more about {w.object_pronoun}? Send YES to {code}"
    )


def description_reply(name: str, gender: str, description: str) -> str:
    w = words_for(gender)
    return f"{first_name(name)} describes {w.reflexive} as {description}"


def unknown_command(code: str) -> str:
    return (
        "Sorry, we did not understand that.\n"
        f"To register SMS start#name#age#gender#county#town to {code}.\n"
        f"To search SMS match#age#town to {code}."
 )
def start_format_error(code: str) -> str:
    return (
        "We could not read your registration.\n"
        f"Please SMS start#name#age#gender#county#town to {code}.\n"
        "E.g., start#John Doe#26#Male#Nakuru#Naivasha"
    )


def start_text_too_long() -> str:
    return "Your name, county or town is too long. Please shorten it and try again."


def invalid_age(min_age: int, max_age: int) -> str:
    return f"Age must be a number from {min_age} to {max_age}. Please try again."


def invalid_gender() -> str:
    return "Gender must be Male or Female. Please try again."


def already_registered_started(name: str, code: str) -> str:
    return (
        f"You are already registered, {first_name(name)}.\n"
        "To add more details SMS details#levelOfEducation#profession"
        f"#maritalStatus#religion#ethnicity to {code}, "
        "or search with match#age#town."
    )


def already_registered_details_done(name: str, code: str) -> str:
    return (
        f"You are already registered, {first_name(name)}.\n"
        "To finish, SMS a brief description of yourself to "
        f"{code} starting with the word MYSELF."
    )


def already_registered_complete(name: str, code: str) -> str:
    return (
        f"You are already registered, {first_name(name)}.\n"
        f"To search for a MPENZI, SMS match#age#town to {code}."
    )