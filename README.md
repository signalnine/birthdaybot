# birthdaybot

Reads a CSV of birthdays and sends an SMS via [textbelt](https://textbelt.com/)
to a single recipient when today matches someone's birthday. Designed to run
from cron.

## Required env vars

Set in `~/.env` (loaded with `python-dotenv`) or in the cron environment:

- `PHONE` -- the phone number to text (the recipient of the reminders).
- `TXTBELT_KEY` -- a textbelt API key.

If either is missing or whitespace-only, the script exits non-zero with a
message naming the missing var.

## CSV format

`birthdays.csv` lives next to `check_bday.py` and must have at least
`Birthday` and `Name` columns:

```
Birthday,Name,Twitter,Instagram
01-01,Name,@twitter handle,instagram username
...
```

`Birthday` is `MM-DD` (zero-padding and single-digit months/days both work,
leading/trailing whitespace is tolerated). Feb 29 birthdays roll to Feb 28
in non-leap years.

The `Twitter` and `Instagram` columns are read but ignored -- they're kept
for historical reasons and may be removed in the future.

## Behavior

For each row whose `Birthday` matches today, the script POSTs to
`https://textbelt.com/text` with the message `"<Name>'s birthday"`. A
delivery confirmation is logged to stdout only after textbelt reports
`success: true`; every failure path (HTTP error, non-JSON body, API-level
failure, network exception) writes to stderr so cron mail surfaces it.
