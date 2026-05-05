from datetime import date
import pytest
from ex07.pricing import calculate_price, calculate_nights, is_weekend

# =============================================================================
# is_weekend
# =============================================================================

def test_is_weekend_saturday():
    # Jan 13 2024 = Saturday (weekday 5) — kills mutants 1 ({6,6}) and 4 (not in)
    assert is_weekend(date(2024, 1, 13)) is True


def test_is_weekend_sunday():
    # Jan 14 2024 = Sunday (weekday 6) — kills mutant 2 ({5,7})
    assert is_weekend(date(2024, 1, 14)) is True


def test_is_weekend_friday_is_not_weekend():
    assert is_weekend(date(2024, 1, 12)) is False


def test_is_weekend_monday_is_not_weekend():
    assert is_weekend(date(2024, 1, 8)) is False


# =============================================================================
# calculate_nights
# =============================================================================

def test_calculate_nights_basic():
    assert calculate_nights(date(2024, 1, 1), date(2024, 1, 3)) == 2


def test_calculate_nights_raises_for_equal_dates():
    # checkout == checkin must raise — kills mutant 5 (< instead of <=)
    # match= also kills mutant 6 (changed error message)
    with pytest.raises(ValueError, match="^Invalid date range$"):
        calculate_nights(date(2024, 1, 1), date(2024, 1, 1))


def test_calculate_nights_raises_for_checkout_before_checkin():
    with pytest.raises(ValueError, match="^Invalid date range$"):
        calculate_nights(date(2024, 1, 5), date(2024, 1, 1))


# =============================================================================
# calculate_price — exact value assertions
# =============================================================================

def test_exact_price_weekdays_only():
    # Mon Jan 8 → Wed Jan 10: 2 nights, no weekends
    # base=200, surcharge=0, cleaning=50, subtotal=250, fee=25, total=275.0
    # Kills mutant 9 (base=nights/rate → 2/100=0.02)
    total = calculate_price(
        date(2024, 1, 8), date(2024, 1, 10),
        nightly_rate=100, cleaning_fee=50, service_fee_pct=0.1,
    )
    assert total == 275.0


def test_exact_price_no_cleaning_no_service():
    # Mon Jan 8 → Wed Jan 10: 2 nights, no weekends, no extras
    # total = 200.0
    total = calculate_price(
        date(2024, 1, 8), date(2024, 1, 10),
        nightly_rate=100, cleaning_fee=0, service_fee_pct=0,
    )
    assert total == 200.0


def test_cleaning_fee_adds_to_total():
    # Kills mutant 26 (subtotal = base + surcharge - cleaning_fee)
    total_with = calculate_price(
        date(2024, 1, 8), date(2024, 1, 10),
        nightly_rate=100, cleaning_fee=50, service_fee_pct=0,
    )
    total_without = calculate_price(
        date(2024, 1, 8), date(2024, 1, 10),
        nightly_rate=100, cleaning_fee=0, service_fee_pct=0,
    )
    assert total_with == total_without + 50.0


def test_saturday_night_surcharge():
    # Sat Jan 13 → Sun Jan 14: 1 night (Saturday only)
    # base=100, weekend_nights=1, surcharge=1*100*0.2=20, subtotal=120, total=120.0
    # Kills: 1,2,4,12,15,16,17,21,22,23,25
    total = calculate_price(
        date(2024, 1, 13), date(2024, 1, 14),
        nightly_rate=100, cleaning_fee=0, service_fee_pct=0,
    )
    assert total == 120.0


def test_sunday_night_surcharge():
    # Sun Jan 14 → Mon Jan 15: 1 night (Sunday only)
    # surcharge=20, total=120.0 — kills mutant 2 ({5,7} doesn't include 6)
    total = calculate_price(
        date(2024, 1, 14), date(2024, 1, 15),
        nightly_rate=100, cleaning_fee=0, service_fee_pct=0,
    )
    assert total == 120.0


def test_two_weekend_nights_surcharge():
    # Sat Jan 13 → Mon Jan 15: 2 nights (Sat + Sun)
    # base=200, weekend_nights=2, surcharge=40, total=240.0
    # Kills mutants 15 (assignment=1), 19 (day+2 skips Sunday)
    total = calculate_price(
        date(2024, 1, 13), date(2024, 1, 15),
        nightly_rate=100, cleaning_fee=0, service_fee_pct=0,
    )
    assert total == 240.0


def test_friday_night_no_surcharge():
    # Fri Jan 12 → Sat Jan 13: 1 night (Friday is NOT a weekend day)
    # base=100, surcharge=0, total=100.0
    # Kills mutant 12 (weekend_nights starts at 1)
    total = calculate_price(
        date(2024, 1, 12), date(2024, 1, 13),
        nightly_rate=100, cleaning_fee=0, service_fee_pct=0,
    )
    assert total == 100.0


def test_six_nights_no_discount():
    # Mon Jan 8 → Sun Jan 14: 6 nights (5 weekday + 1 Sat), checkout=Sunday
    # base=600, surcharge=1*100*0.2=20, subtotal=620, NO 7-day discount, total=620.0
    # Kills mutant 14 (while <= would include Sunday checkout → 2 weekend nights=640)
    total = calculate_price(
        date(2024, 1, 8), date(2024, 1, 14),
        nightly_rate=100, cleaning_fee=0, service_fee_pct=0,
    )
    assert total == 620.0


def test_seven_nights_discount():
    # Mon Jan 8 → Mon Jan 15: exactly 7 nights (5 weekday + Sat + Sun)
    # base=700, surcharge=2*100*0.2=40, subtotal=740, discount=740*0.9=666.0
    # Kills mutants 28 (>7), 29 (>=8), 30 (=0.9), 31 (/=0.9), 32 (*=1.9)
    total = calculate_price(
        date(2024, 1, 8), date(2024, 1, 15),
        nightly_rate=100, cleaning_fee=0, service_fee_pct=0,
    )
    assert total == 666.0


def test_service_fee_applied():
    # Mon Jan 8 → Wed Jan 10: 2 nights, subtotal=200, fee=200*0.1=20, total=220.0
    # Kills mutants 33 (subtotal/fee_pct=2000), 35 (subtotal-fee=180)
    total = calculate_price(
        date(2024, 1, 8), date(2024, 1, 10),
        nightly_rate=100, cleaning_fee=0, service_fee_pct=0.1,
    )
    assert total == 220.0


def test_rounding_to_two_decimal_places():
    # Mon Jan 8 → Tue Jan 9: 1 night, nightly_rate=100, cleaning=1.99, fee_pct=0.07
    # subtotal=101.99, service_fee=101.99*0.07=7.1393, total=109.1293
    # round(2)=109.13 vs round(3)=109.129 — kills mutant 37
    total = calculate_price(
        date(2024, 1, 8), date(2024, 1, 9),
        nightly_rate=100, cleaning_fee=1.99, service_fee_pct=0.07,
    )
    assert total == 109.13


def test_calculate_price_raises_for_equal_dates():
    with pytest.raises(ValueError):
        calculate_price(
            date(2024, 1, 1), date(2024, 1, 1),
            nightly_rate=100, cleaning_fee=50, service_fee_pct=0.1,
        )
