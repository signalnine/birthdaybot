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


def main():
    load_dotenv(os.path.expanduser("~/.env"))

    csv_path = Path(__file__).resolve().parent / "birthdays.csv"
    df = pd.read_csv(csv_path)
    today = datetime.date.today()

    for _, item in df.iterrows():
        if matches_today(item["Birthday"], today):
            resp = requests.post(
                "https://textbelt.com/text",
                {
                    "phone": os.getenv("PHONE"),
                    "message": item["Name"] + "'s birthday",
                    "key": os.getenv("TXTBELT_KEY"),
                },
            )
            print(item["Name"] + "'s birthday")
            print(resp.json())


if __name__ == "__main__":
    main()
