import unittest

import pandas as pd

from pipeline.transform import (
    EXCHANGE_RATE_IDR,
    parse_colors,
    parse_gender,
    parse_price_from_usd_to_idr,
    parse_rating,
    parse_size,
    transform_data,
)


class TestParseHelpers(unittest.TestCase):

    def test_parse_price_from_usd_to_idr_valid(self):
        value = parse_price_from_usd_to_idr("$10.50")
        self.assertEqual(value, int(round(10.5 * EXCHANGE_RATE_IDR)))

    def test_parse_price_from_usd_to_idr_invalid(self):
        self.assertIsNone(parse_price_from_usd_to_idr("Invalid Price"))
        self.assertIsNone(parse_price_from_usd_to_idr(None))

    def test_parse_price_from_usd_to_idr_with_currency_spacing(self):
        value = parse_price_from_usd_to_idr("$ 10.50")
        self.assertEqual(value, int(round(10.5 * EXCHANGE_RATE_IDR)))

    def test_parse_rating_valid_and_invalid(self):
        self.assertEqual(parse_rating("Rating: 4.8 / 5"), 4.8)
        self.assertIsNone(parse_rating("Rating: Invalid"))

    def test_parse_colors_valid_and_invalid(self):
        self.assertEqual(parse_colors("3 Colors"), 3)
        self.assertEqual(parse_colors("1 Color"), 1)
        self.assertIsNone(parse_colors("No Color Info"))

    def test_parse_size_valid_and_invalid(self):
        self.assertEqual(parse_size("Size: M"), "M")
        self.assertEqual(parse_size("Size:   XL"), "XL")
        self.assertIsNone(parse_size(123))

    def test_parse_gender_valid_and_invalid(self):
        self.assertEqual(parse_gender("Gender: Men"), "Men")
        self.assertEqual(parse_gender("Gender: Women"), "Women")
        self.assertIsNone(parse_gender(123))


class TestTransformData(unittest.TestCase):

    def test_transform_data_returns_empty_for_none_input(self):
        result = transform_data(None)
        self.assertTrue(result.empty)

    def test_transform_data_cleans_and_types_data(self):
        raw_data = [
            {
                "Title": "Classic Shirt",
                "Price": "$10.00",
                "Rating": "Rating: 4.5 / 5",
                "Colors": "3 Colors",
                "Size": "Size: M",
                "Gender": "Gender: Men",
                "timestamp": "2026-06-03T00:00:00+00:00",
            },
            {
                "Title": "Classic Shirt",
                "Price": "$10.00",
                "Rating": "Rating: 4.5 / 5",
                "Colors": "3 Colors",
                "Size": "Size: M",
                "Gender": "Gender: Men",
                "timestamp": "2026-06-03T00:00:00+00:00",
            },
            {
                "Title": "Unknown Product",
                "Price": "$20.00",
                "Rating": "Rating: 4.8 / 5",
                "Colors": "2 Colors",
                "Size": "Size: L",
                "Gender": "Gender: Women",
                "timestamp": "2026-06-03T00:00:00+00:00",
            },
            {
                "Title": "Invalid Rating Product",
                "Price": "$8.00",
                "Rating": "Invalid Rating",
                "Colors": "2 Colors",
                "Size": "Size: S",
                "Gender": "Gender: Women",
                "timestamp": "2026-06-03T00:00:00+00:00",
            },
        ]

        result = transform_data(raw_data)

        self.assertEqual(len(result), 1)

        row = result.iloc[0]
        self.assertEqual(row["Title"], "Classic Shirt")
        self.assertEqual(row["Price"], 160000)
        self.assertEqual(row["Rating"], 4.5)
        self.assertEqual(row["Colors"], 3)
        self.assertEqual(row["Size"], "M")
        self.assertEqual(row["Gender"], "Men")

        self.assertEqual(str(result["Title"].dtype), "object")
        self.assertEqual(str(result["Price"].dtype), "float64")
        self.assertEqual(str(result["Rating"].dtype), "float64")
        self.assertEqual(str(result["Colors"].dtype), "int64")
        self.assertEqual(str(result["Size"].dtype), "object")
        self.assertEqual(str(result["Gender"].dtype), "object")

    def test_transform_data_returns_empty_when_required_columns_missing(self):
        raw_data = [{"Title": "Only Title"}]

        result = transform_data(raw_data)

        self.assertTrue(result.empty)

    def test_transform_data_accepts_dataframe_input(self):
        df = pd.DataFrame(
            [
                {
                    "Title": "Hoodie",
                    "Price": "$5.00",
                    "Rating": "Rating: 4.0 / 5",
                    "Colors": "2 Colors",
                    "Size": "Size: L",
                    "Gender": "Gender: Men",
                    "timestamp": "2026-06-03T00:00:00+00:00",
                }
            ]
        )

        result = transform_data(df)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["Title"], "Hoodie")

    def test_transform_data_filters_unknown_product_case_insensitive(self):
        raw_data = [
            {
                "Title": "  UNKNOWN PRODUCT  ",
                "Price": "$10.00",
                "Rating": "Rating: 4.5 / 5",
                "Colors": "2 Colors",
                "Size": "Size: M",
                "Gender": "Gender: Men",
                "timestamp": "2026-06-03T00:00:00+00:00",
            }
        ]

        result = transform_data(raw_data)

        self.assertTrue(result.empty)

    def test_transform_data_drops_rows_with_invalid_parsed_values(self):
        raw_data = [
            {
                "Title": "Valid Product",
                "Price": "$11.00",
                "Rating": "Rating: 4.1 / 5",
                "Colors": "3 Colors",
                "Size": "Size: M",
                "Gender": "Gender: Men",
                "timestamp": "2026-06-03T00:00:00+00:00",
            },
            {
                "Title": "Invalid Price Product",
                "Price": "Not A Price",
                "Rating": "Rating: 4.2 / 5",
                "Colors": "2 Colors",
                "Size": "Size: L",
                "Gender": "Gender: Women",
                "timestamp": "2026-06-03T00:00:00+00:00",
            },
        ]

        result = transform_data(raw_data)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["Title"], "Valid Product")

    def test_transform_data_accepts_shuffled_columns_and_preserves_timestamp(self):
        df = pd.DataFrame(
            [
                {
                    "timestamp": "2026-06-03T12:34:56+00:00",
                    "Gender": "Gender: Women",
                    "Size": "Size: S",
                    "Colors": "1 Color",
                    "Rating": "Rating: 5.0 / 5",
                    "Price": "$7.00",
                    "Title": "Tank Top",
                }
            ]
        )

        result = transform_data(df)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["timestamp"], "2026-06-03T12:34:56+00:00")
        self.assertEqual(result.iloc[0]["Title"], "Tank Top")


if __name__ == "__main__":
    unittest.main()

