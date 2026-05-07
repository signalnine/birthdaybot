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

## Bug fix: non-zero-padded and whitespace birthdays silently skipped (birthdaybot-l6a)

- [x] `matches_today` accepts single-digit month (e.g. "2-14") -> test: `matches_today("2-14", date(2026, 2, 14))` returns True
- [x] `matches_today` accepts single-digit day (e.g. "02-4") -> test: `matches_today("02-4", date(2026, 2, 4))` returns True
- [x] `matches_today` accepts both single-digit (e.g. "2-4") -> test: `matches_today("2-4", date(2026, 2, 4))` returns True
- [x] `matches_today` tolerates leading whitespace -> test: `matches_today(" 02-14", date(2026, 2, 14))` returns True
- [x] `matches_today` tolerates trailing whitespace -> test: `matches_today("02-14 ", date(2026, 2, 14))` returns True
- [x] Feb-29 roll-to-Feb-28 still works with non-canonical formats -> test: `matches_today("2-29", date(2025, 2, 28))` returns True
- [x] Unparseable strings return False (do not crash) -> tests: "not-a-date", "", "13-01", "02-30" all return False

## Bug fix: malformed CSV row aborts whole run (birthdaybot-23x)

- [x] Row with NaN Name is skipped, later matching rows still notified -> test: `test_main_skips_row_with_nan_name_and_continues`
- [x] Row with empty/whitespace Name is skipped, later matching rows still notified -> test: `test_main_skips_row_with_empty_name_and_continues`
- [x] Unexpected exception from `notify()` does not abort remaining rows -> test: `test_main_survives_unexpected_notify_exception`

## Bug fix: whitespace-only env vars silently accepted (birthdaybot-ndt)

- [x] `main()` exits non-zero when PHONE is whitespace-only -> test: `test_main_exits_nonzero_when_phone_is_whitespace_only`
- [x] `main()` exits non-zero when TXTBELT_KEY is whitespace-only -> test: `test_main_exits_nonzero_when_key_is_whitespace_only`
- [x] Leading/trailing whitespace stripped from PHONE before sending -> test: `test_main_strips_whitespace_from_phone_before_sending`
- [x] Leading/trailing whitespace stripped from TXTBELT_KEY before sending -> test: `test_main_strips_whitespace_from_key_before_sending`

## Bug fix: notify() logs delivery before confirming success (birthdaybot-5ip)

- [x] `notify()` does NOT write a delivery-confirmation line to stdout when HTTP status >= 400 -> test: `test_notify_does_not_log_success_on_http_error`
- [x] `notify()` does NOT write a delivery-confirmation line to stdout when body reports `success: false` -> test: `test_notify_does_not_log_success_on_api_failure`
- [x] `notify()` does NOT write a delivery-confirmation line to stdout when body is a non-dict (null/list/scalar) -> test: `test_notify_does_not_log_success_on_non_dict_body`
- [x] `notify()` writes a confirmation line to stdout only after `success: true` is observed -> test: `test_notify_logs_success_only_after_confirmation`
- [x] All failure-path messages from `notify()` go to stderr, not stdout -> test: `test_notify_failure_messages_go_to_stderr`

## Bug fix: missing or malformed CSV crashes with raw traceback (birthdaybot-v0z)

- [x] `main()` exits non-zero with a single-line stderr error when birthdays.csv is missing -> test: `test_main_exits_nonzero_when_csv_missing`
- [x] `main()` exits non-zero with a single-line stderr error when CSV is missing the 'Birthday' column -> test: `test_main_exits_nonzero_when_csv_missing_birthday_column`
- [x] `main()` exits non-zero with a single-line stderr error when CSV is missing the 'Name' column -> test: `test_main_exits_nonzero_when_csv_missing_name_column`
- [x] No raw pandas traceback escapes any of the above paths -> verified by the same tests asserting a clean single-line message

## Bug fix: malformed CSV crashes with raw pandas traceback (birthdaybot-d74)

- [x] `main()` exits non-zero with single-line stderr on `pd.errors.ParserError` -> test: `test_main_exits_nonzero_on_csv_parser_error`
- [x] `main()` exits non-zero with single-line stderr on `pd.errors.EmptyDataError` -> test: `test_main_exits_nonzero_on_csv_empty_data_error`
- [x] `main()` exits non-zero with single-line stderr on `UnicodeDecodeError` -> test: `test_main_exits_nonzero_on_csv_unicode_decode_error`

## Bug fix: main() exits 0 when every notification fails (birthdaybot-266)

- [x] `main()` exits non-zero when every notify() attempt returns False -> test: `test_main_exits_nonzero_when_all_notify_attempts_fail`
- [x] `main()` exits non-zero when every notify() attempt raises -> test: `test_main_exits_nonzero_when_all_notify_attempts_raise`
- [x] `main()` exits zero when at least one notify() attempt succeeds -> test: `test_main_exits_zero_when_at_least_one_notify_succeeds`
- [x] `main()` exits zero when no rows match today (no attempts) -> test: `test_main_exits_zero_when_no_birthdays_today`

## Bug fix: rows with non-string Birthday silently skipped (birthdaybot-83f)

- [x] Row with NaN Birthday but present Name produces a stderr warning -> test: `test_main_warns_when_birthday_is_nan_but_name_present`
- [x] Row with int Birthday (pandas type-inferred from "0704") but present Name produces a stderr warning -> test: `test_main_warns_when_birthday_is_int_but_name_present`
- [x] Fully empty row (both fields missing) stays silent to avoid noise on trailing CSV blank lines -> test: `test_main_silent_on_fully_empty_row`

## Doc fix: README contradicts implementation (birthdaybot-oz5)

- [x] README describes SMS delivery via textbelt (not Twitter/Instagram) -> verified by reading README
- [x] README names the required env vars `PHONE` and `TXTBELT_KEY` -> verified by reading README
- [x] README either drops the unused Twitter/Instagram CSV columns or documents that they are ignored -> verified by reading README
