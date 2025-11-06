from pydantic_extra_types.semantic_version import SemanticVersion

DATETIME_FORMAT = r"%m/%d/%Y %H:%M:%S"
NANOSECONDS_DAY = 86400 * 10**9
NANOSECONDS_HOUR = 3600 * 10**9
NANOSECONDS_MINUTE = 60 * 10**9
NANOSECONDS_SECOND = 10**9
MINIMUM_LSS_VERSION = SemanticVersion(1, 6, 0)
