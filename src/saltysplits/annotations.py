import re
from pandas import Timedelta
from datetime import datetime
from pydantic import BeforeValidator, PlainSerializer, AfterValidator
from packaging.version import Version
from typing import Optional, Annotated, List
from saltysplits.constants import (
    DATETIME_FORMAT,
    NANOSECONDS_DAY,
    NANOSECONDS_HOUR,
    NANOSECONDS_MINUTE,
    NANOSECONDS_SECOND,
    MINIMUM_LSS_VERSION,
)


def decode_time(value: str) -> Timedelta:
    """
    Decodes a string using LSS` time representation as a pandas.Timedelta object (including optional days prefix)

    Args:
        value (str): String using LSS' time representation (e.g. "1.01:55:11.1422649")

    Returns:
        Timedelta: Timedelta representation of the input string
    """

    pattern = re.compile(
        r"^(?:(?P<days>\d+)\.)?(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+)(?:\.(?P<fraction>\d+))?$"
    )
    match = pattern.match(value)
    assert match, (
        "Invalid time format, expected 'HH:MM:SS' (with optional days prefix and fraction suffix)"
    )
    groups = match.group("days", "hours", "minutes", "seconds", "fraction")
    days, hours, minutes, seconds, fraction = map(lambda x: int(x) if x else 0, groups)
    nanoseconds = fraction * 100

    return Timedelta(
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        nanoseconds=nanoseconds,
    )


def parse_timedelta(timedelta: Timedelta) -> List[int]:
    """
    Decomposes a Timedelta object into its equivalent days, hours, minutes, seconds
    and nanoseconds. Divmod is used to prevent floating-point errors

    Args:
        timedelta (Timedelta): Timedelta object to decompose

    Returns:
        List[int]: Integer list containing days, hours, minutes, seconds and nanoseconds
    """

    days, remainder = divmod(timedelta.value, NANOSECONDS_DAY)
    hours, remainder = divmod(remainder, NANOSECONDS_HOUR)
    minutes, remainder = divmod(remainder, NANOSECONDS_MINUTE)
    seconds, remainder = divmod(remainder, NANOSECONDS_SECOND)
    nanoseconds = remainder // 100
    return days, hours, minutes, seconds, nanoseconds


def encode_time(content: Timedelta, include_ns: bool = True) -> str:
    """
    Encodes a Timedelta object as the same string format used in the LSS files (i.e. 'HH:MM:SS' with optional days prefix and fractional seconds suffix)

    Args:
        content (Timedelta): Timedelta object to represent as string using LSS' time representation
        include_ns (bool, optional): Whether to include nanoseconds in the formatted string. Defaults to True.

    Returns:
        str: LSS string representation of input Timedelta object
    """

    # optionally adds n_nanoseconds suffix but only adds n_days prefix if not 0
    days, hours, minutes, seconds, nanoseconds = parse_timedelta(timedelta=content)
    delta_string = f"{hours:02}:{minutes:02}:{seconds:02}"
    delta_string = f"{delta_string}.{nanoseconds:07}" if include_ns else delta_string
    delta_string = f"{days}.{delta_string}" if days else delta_string
    return delta_string


def encode_offset(content: Timedelta) -> str:
    """
    Encodes a Timedelta object as the same string format used in the LSS files (i.e. 'HH:MM:SS' with optional days prefix and fractional seconds suffix)

    Args:
        content (Timedelta): Timedelta object to represent as string using LSS' time representation
        include_ns (bool, optional): Whether to include nanoseconds in the formatted string. Defaults to True.

    Returns:
        str: LSS string representation of input Timedelta object
    """

    # only adds n_nanoseconds suffix and n_days prefix if not 0
    days, hours, minutes, seconds, nanoseconds = parse_timedelta(timedelta=content)
    delta_string = f"{hours:02}:{minutes:02}:{seconds:02}"
    delta_string = f"{delta_string}.{nanoseconds:07}" if nanoseconds else delta_string
    delta_string = f"{days}.{delta_string}" if days else delta_string
    return delta_string


def decode_datetime(value: str) -> datetime:
    return datetime.strptime(value, DATETIME_FORMAT)


def encode_datetime(content: datetime) -> str:
    return content.strftime(DATETIME_FORMAT)


def verify_version(lss_version: Version) -> Version:
    if lss_version < MINIMUM_LSS_VERSION:
        raise ValueError(
            f"Minimum LSS file version is {MINIMUM_LSS_VERSION}. Consider exporting your {lss_version} LSS file with LiveSplit to reencode it to a more recent version"
        )
    return lss_version


TimeOptional = Annotated[
    Optional[Timedelta],
    PlainSerializer(encode_time, when_used="unless-none"),
    BeforeValidator(decode_time),
]

OffsetOptional = Annotated[
    Optional[Timedelta],
    PlainSerializer(encode_offset, when_used="unless-none"),
    BeforeValidator(decode_time),
]

DateTime = Annotated[
    datetime,
    PlainSerializer(encode_datetime, when_used="unless-none"),
    BeforeValidator(decode_datetime),
]


SBool = Annotated[
    bool,
    PlainSerializer(lambda x: str(x), when_used="unless-none"),
]

LssVersion = Annotated[
    Version,
    BeforeValidator(Version),
    AfterValidator(verify_version),
    PlainSerializer(lambda x: str(x), when_used="always"),
]
