#!/usr/bin/python3

import calendar
import datetime
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


def matches_today(bday: str, today: datetime.date) -> bool:
    """Return True if the CSV birthday string matches today's date.

    Feb 29 birthdays roll to Feb 28 in non-leap years so they aren't
    silently skipped for three years out of four.
    """
    if bday == today.strftime("%m-%d"):
        return True
    if (
        bday == "02-29"
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
    if not body.get("success"):
        print(f"textbelt rejected message for {name}: {body.get('error')}")
        return False
    return True


def main():
    load_dotenv(os.path.expanduser("~/.env"))

    csv_path = Path(__file__).resolve().parent / "birthdays.csv"
    df = pd.read_csv(csv_path)
    today = datetime.date.today()
    phone = os.getenv("PHONE")
    key = os.getenv("TXTBELT_KEY")

    for _, item in df.iterrows():
        if matches_today(item["Birthday"], today):
            notify(item["Name"], phone, key)


if __name__ == "__main__":
    main()
