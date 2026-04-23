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

## Bug fix: textbelt API-level failures

- [x] `notify` returns False when textbelt response body has `success: false` -> test: mock post returns `{"success": false, "error": "Out of quota"}`, assert returns False
- [x] `notify` returns False on non-2xx HTTP status -> test: mock post returns 500, assert returns False
- [x] `notify` still returns True on `{"success": true, ...}` 200 response -> test: mock post returns `{"success": true, "textId": "abc", "quotaRemaining": 10}`, assert returns True

## Bug fix: non-dict JSON bodies

- [x] `notify` returns False when body is JSON null -> test: mock post returns `None`, assert returns False (no AttributeError)
- [x] `notify` returns False when body is a JSON list -> test: mock post returns `["unexpected"]`, assert returns False
- [x] `notify` returns False when body is a JSON scalar -> test: mock post returns `"surprise string"`, assert returns False

## Bug fix: missing env vars silently no-op (birthdaybot-36q)

- [x] `main()` exits non-zero when PHONE is unset -> test: clear PHONE env, call main(), expect SystemExit with non-zero code
- [x] `main()` exits non-zero when TXTBELT_KEY is unset -> test: clear TXTBELT_KEY env, call main(), expect SystemExit with non-zero code
- [x] Error message names the missing variable -> test: capture stderr, assert it mentions "PHONE" or "TXTBELT_KEY"
- [x] `main()` does not call notify() when env vars are missing -> test: mock requests.post, assert not called
- [x] `main()` runs normally when both env vars are set -> test: with PHONE and TXTBELT_KEY set, main() completes without SystemExit
