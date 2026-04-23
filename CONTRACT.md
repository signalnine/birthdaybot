# Bug fix contract: Feb 29 birthdays

## Behaviors

- [x] Exact `%m-%d` match triggers notification -> test: `matches_today("07-04", date(2026, 7, 4))` returns True
- [x] Non-matching date does not trigger -> test: `matches_today("07-04", date(2026, 7, 5))` returns False
- [x] Feb 29 birthday matches Feb 29 in a leap year -> test: `matches_today("02-29", date(2024, 2, 29))` returns True
- [x] Feb 29 birthday matches Feb 28 in a non-leap year -> test: `matches_today("02-29", date(2025, 2, 28))` returns True
- [x] Feb 29 birthday does NOT match Feb 28 in a leap year -> test: `matches_today("02-29", date(2024, 2, 28))` returns False
- [x] Feb 28 birthday matches Feb 28 regardless of year -> test: `matches_today("02-28", date(2025, 2, 28))` returns True
- [x] Feb 28 birthday does not leak into Feb 29 -> test: `matches_today("02-28", date(2024, 2, 29))` returns False
- [x] Script still runs end-to-end -> smoke test: `python3 check_bday.py` with today=2026-04-22 exits cleanly
