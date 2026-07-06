REQUIRED_COLUMNS = {
    "Title",
    "Price",
    "Rating",
    "Colors",
    "Size",
    "Gender",
    "timestamp",
}

class ValidationError(Exception):
    """Raised when raw dataset validation fails."""

def validate_raw_dataset(rows: list[dict]) -> None:
    """
    Validate raw extracted dataset.

    Raises:
        ValidationError:
            If the dataset does not satisfy validation rules.
    """

    if not rows:
        raise ValidationError("Raw dataset is empty.")

    for index, row in enumerate(rows):

        if not isinstance(row, dict):
            raise ValidationError(
                f"Row {index} is not a dictionary."
            )

        missing = REQUIRED_COLUMNS - row.keys()

        if missing:
            raise ValidationError(
                f"Row {index} is missing required columns: "
                f"{sorted(missing)}"
            )