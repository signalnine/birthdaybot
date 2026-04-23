from datetime import date

from check_bday import matches_today


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
