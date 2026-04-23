from datetime import date
from unittest.mock import patch, MagicMock

import pytest
import requests

from check_bday import main, matches_today, notify


def test_exact_match():
    assert matches_today("07-04", date(2026, 7, 4))


def test_non_match():
    assert not matches_today("07-04", date(2026, 7, 5))


def test_feb_29_in_leap_year():
    assert matches_today("02-29", date(2024, 2, 29))


def test_feb_29_rolls_to_feb_28_in_non_leap_year():
    assert matches_today("02-29", date(2025, 2, 28))


def test_feb_29_does_not_match_feb_28_in_leap_year():
    assert not matches_today("02-29", date(2024, 2, 28))


def test_feb_28_matches_feb_28_any_year():
    assert matches_today("02-28", date(2025, 2, 28))
    assert matches_today("02-28", date(2024, 2, 28))


def test_feb_28_does_not_match_feb_29():
    assert not matches_today("02-28", date(2024, 2, 29))


def test_single_digit_month_matches():
    assert matches_today("2-14", date(2026, 2, 14))


def test_single_digit_day_matches():
    assert matches_today("02-4", date(2026, 2, 4))


def test_single_digit_month_and_day_matches():
    assert matches_today("2-4", date(2026, 2, 4))


def test_leading_whitespace_matches():
    assert matches_today(" 02-14", date(2026, 2, 14))


def test_trailing_whitespace_matches():
    assert matches_today("02-14 ", date(2026, 2, 14))


def test_single_digit_feb_29_rolls_to_feb_28_in_non_leap_year():
    assert matches_today("2-29", date(2025, 2, 28))


def test_whitespace_feb_29_rolls_to_feb_28_in_non_leap_year():
    assert matches_today(" 02-29 ", date(2025, 2, 28))


def test_non_date_string_does_not_match():
    assert not matches_today("not-a-date", date(2026, 2, 14))


def test_empty_string_does_not_match():
    assert not matches_today("", date(2026, 2, 14))


def test_invalid_month_does_not_match():
    assert not matches_today("13-01", date(2026, 1, 13))


def test_invalid_day_does_not_match():
    assert not matches_today("02-30", date(2026, 2, 1))


def _ok_response():
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"success": True, "textId": "abc", "quotaRemaining": 10}
    return resp


def test_notify_passes_timeout_to_requests():
    with patch("check_bday.requests.post") as mock_post:
        mock_post.return_value = _ok_response()
        notify("Tony", "555-1234", "key")
        assert "timeout" in mock_post.call_args.kwargs


def test_notify_returns_false_on_timeout():
    with patch("check_bday.requests.post", side_effect=requests.Timeout):
        assert notify("Tony", "555-1234", "key") is False


def test_notify_returns_false_on_connection_error():
    with patch("check_bday.requests.post", side_effect=requests.ConnectionError):
        assert notify("Tony", "555-1234", "key") is False


def test_notify_returns_true_on_success():
    with patch("check_bday.requests.post") as mock_post:
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"success": True, "textId": "abc", "quotaRemaining": 10}
        mock_post.return_value = resp
        assert notify("Tony", "555-1234", "key") is True


def test_notify_returns_false_when_api_reports_failure():
    with patch("check_bday.requests.post") as mock_post:
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"success": False, "error": "Out of quota"}
        mock_post.return_value = resp
        assert notify("Tony", "555-1234", "key") is False


def test_notify_returns_false_on_http_error_status():
    with patch("check_bday.requests.post") as mock_post:
        resp = MagicMock()
        resp.status_code = 500
        resp.json.return_value = {}
        mock_post.return_value = resp
        assert notify("Tony", "555-1234", "key") is False


def test_notify_returns_false_when_body_is_null():
    with patch("check_bday.requests.post") as mock_post:
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = None
        mock_post.return_value = resp
        assert notify("Tony", "555-1234", "key") is False


def test_notify_returns_false_when_body_is_list():
    with patch("check_bday.requests.post") as mock_post:
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = ["unexpected"]
        mock_post.return_value = resp
        assert notify("Tony", "555-1234", "key") is False


def test_notify_returns_false_when_body_is_scalar():
    with patch("check_bday.requests.post") as mock_post:
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = "surprise string"
        mock_post.return_value = resp
        assert notify("Tony", "555-1234", "key") is False


def test_main_exits_nonzero_when_phone_missing(monkeypatch, capsys):
    monkeypatch.delenv("PHONE", raising=False)
    monkeypatch.setenv("TXTBELT_KEY", "testkey")
    monkeypatch.setattr("check_bday.load_dotenv", lambda *a, **kw: None)
    with patch("check_bday.requests.post") as mock_post:
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code != 0
        mock_post.assert_not_called()
    err = capsys.readouterr().err
    assert "PHONE" in err


def test_main_exits_nonzero_when_key_missing(monkeypatch, capsys):
    monkeypatch.setenv("PHONE", "555-1234")
    monkeypatch.delenv("TXTBELT_KEY", raising=False)
    monkeypatch.setattr("check_bday.load_dotenv", lambda *a, **kw: None)
    with patch("check_bday.requests.post") as mock_post:
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code != 0
        mock_post.assert_not_called()
    err = capsys.readouterr().err
    assert "TXTBELT_KEY" in err


def test_main_runs_when_env_vars_present(monkeypatch):
    monkeypatch.setenv("PHONE", "555-1234")
    monkeypatch.setenv("TXTBELT_KEY", "testkey")
    monkeypatch.setattr("check_bday.load_dotenv", lambda *a, **kw: None)
    with patch("check_bday.requests.post") as mock_post:
        mock_post.return_value = _ok_response()
        main()
