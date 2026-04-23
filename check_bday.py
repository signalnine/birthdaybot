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
    """Send a birthday text. Returns True on success, False on network failure.

    Wrapped in try/except so a single network error doesn't halt the loop
    and miss other birthdays that day. Timeout prevents the cron job from
    hanging indefinitely if textbelt is unresponsive.
    """
    try:
        resp = requests.post(
            "https://textbelt.com/text",
            {"phone": phone, "message": name + "'s birthday", "key": key},
            timeout=REQUEST_TIMEOUT,
        )
        print(name + "'s birthday")
        print(resp.json())
        return True
    except requests.RequestException as exc:
        print(f"Failed to notify for {name}: {exc}")
        return False


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
