#!/usr/bin/python3

import calendar
import datetime
import os
import sys
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


def _parse_bday(bday: str) -> tuple[int, int] | None:
    """Parse a CSV birthday string into (month, day), tolerating whitespace
    and non-zero-padded values. Returns None if unparseable or invalid.
    """
    if not isinstance(bday, str):
        return None
    parts = bday.strip().split("-")
    if len(parts) != 2:
        return None
    try:
        month = int(parts[0])
        day = int(parts[1])
    except ValueError:
        return None
    try:
        datetime.date(2000, month, day)
    except ValueError:
        return None
    return month, day


def matches_today(bday: str, today: datetime.date) -> bool:
    """Return True if the CSV birthday string matches today's date.

    Feb 29 birthdays roll to Feb 28 in non-leap years so they aren't
    silently skipped for three years out of four. Leading/trailing whitespace
    and non-zero-padded month or day (e.g. "2-14") are accepted.
    """
    parsed = _parse_bday(bday)
    if parsed is None:
        return False
    month, day = parsed
    if (month, day) == (today.month, today.day):
        return True
    if (
        (month, day) == (2, 29)
        and today.month == 2
        and today.day == 28
        and not calendar.isleap(today.year)
    ):
        return True
    return False


REQUEST_TIMEOUT = 10


def notify(name: str, phone: str, key: str) -> bool:
    """Send a birthday text. Returns True only on confirmed delivery.

    textbelt returns 200 with `{"success": false, "error": "..."}` for
    application-level failures (out of quota, bad key, invalid phone), so
    a 2xx status alone is not enough -- the response body must also report
    success.
    """
    try:
        resp = requests.post(
            "https://textbelt.com/text",
            {"phone": phone, "message": name + "'s birthday", "key": key},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        print(f"Failed to notify for {name}: {exc}")
        return False

    print(name + "'s birthday")

    if resp.status_code >= 400:
        print(f"textbelt returned HTTP {resp.status_code} for {name}")
        return False

    try:
        body = resp.json()
    except ValueError:
        print(f"textbelt returned non-JSON response for {name}")
        return False

    print(body)
    if not isinstance(body, dict):
        print(f"textbelt returned unexpected JSON shape for {name}: {type(body).__name__}")
        return False
    if not body.get("success"):
        print(f"textbelt rejected message for {name}: {body.get('error')}")
        return False
    return True


def main():
    load_dotenv(os.path.expanduser("~/.env"))

    phone = (os.getenv("PHONE") or "").strip()
    key = (os.getenv("TXTBELT_KEY") or "").strip()
    missing = [name for name, val in (("PHONE", phone), ("TXTBELT_KEY", key)) if not val]
    if missing:
        print(f"Missing required env var(s): {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    csv_path = Path(__file__).resolve().parent / "birthdays.csv"
    df = pd.read_csv(csv_path)
    today = datetime.date.today()

    for _, item in df.iterrows():
        if not matches_today(item["Birthday"], today):
            continue
        name = item["Name"]
        if not isinstance(name, str) or not name.strip():
            print(
                f"Skipping row with missing or non-string Name (Birthday={item['Birthday']!r})",
                file=sys.stderr,
            )
            continue
        try:
            notify(name.strip(), phone, key)
        except Exception as exc:
            # One surprise from notify() must not skip remaining birthdays for today.
            print(f"Unexpected error notifying {name!r}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
