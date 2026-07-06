import pytest

from pipeline.validation import (
    validate_raw_dataset,
    ValidationError,
    REQUIRED_COLUMNS,
)

@pytest.fixture
def valid_row():
    return {
        "Title": "Test Product",
        "Price": "100",
        "Rating": "4.5",
        "Colors": "Blue",
        "Size": "M",
        "Gender": "Men",
        "timestamp": "2024-01-01T00:00:00",
    }

def test_validate_raw_dataset_with_valid_data(valid_row):
    """Test that a valid row passes validation."""
    try:
        validate_raw_dataset([valid_row])
    except ValidationError:
        pytest.fail("validate_raw_dataset() raised ValidationError unexpectedly!")

def test_validate_raw_dataset_with_empty_data():
    """Test that empty data raises a ValidationError."""
    with pytest.raises(ValidationError, match="Raw dataset is empty."):
        validate_raw_dataset([])

def test_validate_raw_dataset_with_invalid_row_type():
    """Test that a non-dictionary row raises a ValidationError."""
    with pytest.raises(ValidationError, match="Row 0 is not a dictionary."):
        validate_raw_dataset(["not a dict"])  # type: ignore

def test_validate_raw_dataset_with_missing_columns(valid_row):
    """Test that a row with missing columns raises a ValidationError."""
    for col in REQUIRED_COLUMNS:
        invalid_row = valid_row.copy()
        del invalid_row[col]
        with pytest.raises(ValidationError, match=f"Row 0 is missing required columns: .*'{col}'.*"):
            validate_raw_dataset([invalid_row])