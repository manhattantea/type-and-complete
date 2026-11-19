# python 650_datetime_timezones_and_zoneinfo.py

from datetime import UTC, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def naive_vs_aware_and_utc_now() -> None:

    # Python's datetime objects come in two incompatible flavors:
    # - Naive (dt.tzinfo is None): plain calendar and wall-clock numbers with no
    #   timezone attached. You cannot tell which physical instant on Earth a
    #   naive datetime represents.
    # - Aware (dt.tzinfo is not None): anchored to a UTC offset or timezone rule,
    #   pinpointing an unambiguous instant in physical time.
    #
    # Mixing naive and aware datetimes in subtraction or comparisons (<, >)
    # immediately raises TypeError: can't subtract offset-naive and offset-aware
    # datetimes. Worse, bare datetime.now() returns a naive local wall-clock
    # time, and the legacy datetime.utcnow() (deprecated in Python 3.12) also
    # returned a naive datetime whose .timestamp() method wrongly assumed local
    # system time.
    #
    #     Suppose local_naive = datetime.now() and utc_aware = datetime.now(UTC).
    #     local_naive.tzinfo is None, while utc_aware.tzinfo is datetime.timezone.utc.
    #     Subtracting utc_aware - local_naive raises TypeError instead of guessing.
    #
    # The modern rule is simple: always construct timestamps with datetime.now(UTC),
    # store and compute in aware UTC, and convert to local time only at display.

    print("Naive tzinfo:", datetime.now().tzinfo, "| Aware tzinfo:", datetime.now(UTC).tzinfo)

    # Capture now_utc = datetime.now(UTC) and local_naive = datetime.now().
    # Print both objects and their .tzinfo attributes, then wrap
    # _diff = now_utc - local_naive inside try ... except TypeError as err: and
    # print the exact error message.


    # Also verify comparison behavior between naive and aware datetimes:
    # try comparing now_utc < local_naive inside try ... except TypeError as err:
    # and print the caught error, then compare now_utc == local_naive (notice ==
    # returns False instead of raising TypeError!).


    # Try uncommenting the line below to observe the raw unhandled TypeError:
    # _bad_diff = datetime.now(UTC) - datetime.now()


def timedelta_iso_parsing_and_strptime_strftime() -> None:

    # timedelta(days=..., hours=..., minutes=..., seconds=...) represents an
    # elapsed duration. Adding or subtracting a timedelta shifts a datetime, and
    # subtracting two aware datetimes produces a timedelta whose .total_seconds()
    # returns the exact float duration in seconds.
    #
    # For text serialization, choose between two distinct tools:
    # - .isoformat() and datetime.fromisoformat(s): fast, unambiguous ISO-8601
    #   round-tripping that preserves any timezone offset (including trailing "Z"
    #   for UTC natively since Python 3.11).
    # - datetime.strptime(s, fmt) and dt.strftime(fmt): format-code parsers and
    #   formatters for legacy or human-facing non-ISO strings like "19/11/2026 14:30".
    #
    #     Suppose stamp = "2026-11-19T14:30:00Z".
    #     datetime.fromisoformat(stamp) returns an aware UTC datetime directly.
    #     By contrast, "19/11/2026 14:30" is not ISO-8601, so you parse it with
    #     datetime.strptime(text, "%d/%m/%Y %H:%M") and attach .replace(tzinfo=UTC).

    starter_utc = datetime.now(UTC)
    print("Starter ISO:", starter_utc.isoformat())

    # Capture now_utc = datetime.now(UTC), compute
    # expires_at = now_utc + timedelta(hours=2, minutes=30), format
    # iso_str = expires_at.isoformat(), parse it back with
    # parsed_dt = datetime.fromisoformat(iso_str), and print iso_str, parsed_dt,
    # and (parsed_dt - now_utc).total_seconds().


    # Parse "2026-11-19T08:15:00Z" with datetime.fromisoformat(...) and verify
    # parsed.tzinfo is UTC. Then parse legacy_text = "19/11/2026 08:15" using
    # datetime.strptime(legacy_text, "%d/%m/%Y %H:%M").replace(tzinfo=UTC) and
    # format it back for display using .strftime("%Y-%m-%d %H:%M %Z").


    # Compute the elapsed timedelta between two aware datetimes 90 minutes apart
    # and print .days, .seconds, and .total_seconds() (notice .seconds only holds
    # the sub-day remainder, while .total_seconds() includes full days too).


def timezones_astimezone_and_zoneinfo() -> None:

    # Calling .astimezone(tz) on an aware datetime returns a new aware datetime
    # expressing the exact same physical instant in another timezone or offset.
    # Because both represent the same moment in time, utc_dt == converted_dt
    # evaluates to True even though their .hour and .tzinfo differ:
    #
    #     Suppose utc_dt = datetime(2026, 11, 19, 12, 0, tzinfo=UTC).
    #     plus_two = utc_dt.astimezone(timezone(timedelta(hours=2)))
    #     plus_two.hour is 14, yet utc_dt == plus_two is True.
    #
    # zoneinfo.ZoneInfo("America/New_York") uses the standard IANA timezone
    # database so Daylight Saving Time transitions work automatically. Note one
    # Windows nuance: Linux and macOS ship system IANA tzdata files, whereas
    # Windows does not—without the optional tzdata package installed, calling
    # ZoneInfo("America/New_York") raises ZoneInfoNotFoundError. Fixed offsets
    # like timezone(timedelta(hours=2)) and UTC always work everywhere in stdlib.

    fixed_plus_2 = timezone(timedelta(hours=2))
    print("Starter fixed offset:", datetime.now(UTC).astimezone(fixed_plus_2).isoformat())

    # Convert now_utc = datetime.now(UTC) to timezone(timedelta(hours=2)) using
    # converted_dt = now_utc.astimezone(timezone(timedelta(hours=2))). Print both
    # datetimes and verify now_utc == converted_dt is True.


    # Wrap now_utc.astimezone(ZoneInfo("America/New_York")) inside
    # try ... except ZoneInfoNotFoundError: so it prints the New York local time
    # when IANA tzdata is available and prints a short fallback note otherwise.


    # Create a UTC datetime right before and after a US spring-forward DST jump
    # (for example datetime(2026, 3, 8, 6, 30, tzinfo=UTC) and + timedelta(hours=1))
    # inside try ... except ZoneInfoNotFoundError: and convert both with
    # ZoneInfo("America/New_York") to observe the offset shift from -05:00 to -04:00.


def main() -> None:

    print("=== 1. Naive vs aware datetimes and UTC now ===")
    naive_vs_aware_and_utc_now()

    print("\n=== 2. timedelta, fromisoformat, and strptime/strftime ===")
    timedelta_iso_parsing_and_strptime_strftime()

    print("\n=== 3. .astimezone(), fixed offsets, and ZoneInfo ===")
    timezones_astimezone_and_zoneinfo()


if __name__ == "__main__":
    main()
