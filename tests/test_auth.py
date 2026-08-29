from app.auth import make_token


def test_make_token_length():
    assert len(make_token()) == 24
