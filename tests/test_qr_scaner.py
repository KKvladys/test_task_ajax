import pytest

from unittest.mock import patch

from scanner_handler import CheckQr


@pytest.fixture
def check_qr():
    return CheckQr()


@pytest.mark.parametrize(
    "qr_code, expected_color",
    [
        ("1a!", "Red"),
        ("1@c45", "Green"),
        ("1234567", "Fuzzy Wuzzy"),
    ]
)
def test_check_len_color_valid(check_qr, qr_code, expected_color):
    """
    Test checks if the correct color is
    returned for different QR code lengths.
    """
    color = check_qr.check_len_color(qr_code)
    assert color == expected_color


@pytest.mark.parametrize(
    "qr_code",
    [
        "",
        "abcd",
        "abcttr",
        "1",
        "w" * 100
    ]
)
def test_check_len_color_invalid(check_qr, qr_code):
    """
    Tests if the check_len_color method for invalid QR codes.
    """
    color = check_qr.check_len_color(qr_code)
    assert color is None


@patch.object(CheckQr, "check_in_db", return_value=None)
def test_check_scanned_device_not_in_db(mock_check_in_db, check_qr):
    """
    Verifies error handling when the
    scanned QR code isn't found in the database.
    """
    qr_code = "123"
    with patch.object(check_qr, "send_error") as mock_send_error:
        check_qr.check_scanned_device(qr_code)
        mock_send_error.assert_called_once_with("Not in DB")


@pytest.mark.parametrize("qr_code, expected_error", [
    ("abcd", "Error: Wrong qr length 4"),
    ("xy", "Error: Wrong qr length 2"),
])
@patch.object(CheckQr, "check_in_db", return_value=None)
def test_send_error_called(mock_check_in_db, check_qr, qr_code, expected_error):
    """
    Checks that the correct error message is
    triggered for incorrect QR code lengths.
    """
    with patch.object(check_qr, "send_error") as mock_send_error:
        check_qr.check_scanned_device(qr_code)
        mock_send_error.assert_any_call(expected_error)


@patch.object(CheckQr, "check_in_db", return_value=True)
def test_check_scanned_device_success(mock_check_in_db, check_qr):
    """
    Tests successful device scanning when the
    QR code is valid and present in the database.
    """
    qr_code = "123"
    with patch.object(check_qr, "can_add_device") as mock_can_add_device:
        check_qr.check_scanned_device(qr_code)
        mock_can_add_device.assert_called_once_with(f"hallelujah {qr_code}")
