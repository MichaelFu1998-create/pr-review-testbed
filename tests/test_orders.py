from app.orders import price_total


def test_price_total_returns_a_number():
    assert isinstance(price_total(10.0, 2), float)
