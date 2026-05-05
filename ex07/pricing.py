from datetime import date

WEEKEND_DAYS = {5, 6}


def is_weekend(d: date) -> bool:
    return d.weekday() in WEEKEND_DAYS


def calculate_nights(checkin: date, checkout: date) -> int:
    if checkout <= checkin:
        raise ValueError("Invalid date range")
    return (checkout - checkin).days


def calculate_price(checkin, checkout, nightly_rate, cleaning_fee, service_fee_pct):
    nights = calculate_nights(checkin, checkout)
    base = nights * nightly_rate
    current = checkin
    weekend_nights = 0
    while current < checkout:
        if is_weekend(current):
            weekend_nights += 1
        current = current.replace(day=current.day + 1)
    weekend_surcharge = weekend_nights * nightly_rate * 0.2
    subtotal = base + weekend_surcharge + cleaning_fee
    if nights >= 7:
        subtotal *= 0.9
    service_fee = subtotal * service_fee_pct
    total = subtotal + service_fee
    return round(total, 2)
