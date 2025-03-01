import pytest
from scanner_handler import CheckQr


@pytest.fixture
def check_qr():
    return CheckQr()


@pytest.mark.parametrize(
    "qr_code, expected_color",
    [
    ("abc", "Red"),
    ("12345", "Green"),
    ("abcdefg", "Fuzzy Wuzzy"),
    ]
)
def test_check_len_color_valid(check_qr, qr_code, expected_color):
    color = check_qr.check_len_color(qr_code)
    assert color == expected_color


@pytest.mark.parametrize(
    "qr_code",
    [   "",
        "abcd",
        "123456",
        "1",
        "s" * 100
    ]
)
def test_check_len_color_invalid(check_qr, qr_code):
    color = check_qr.check_len_color(qr_code)
    assert color is None
