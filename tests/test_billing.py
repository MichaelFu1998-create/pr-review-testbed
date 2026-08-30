from app.billing import apply_discount


def test_apply_discount_reduces_the_amount():
    assert apply_discount(100.0, 10) < 100.0
