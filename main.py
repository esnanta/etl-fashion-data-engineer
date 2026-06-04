import os

from dotenv import load_dotenv

from utils.extract import DEFAULT_BASE_URL, scrape_data
from utils.transform import transform_data
from utils.load import save_to_csv, save_to_google_sheets


load_dotenv()

def _print_scrape_progress(current, total, collected_rows, page, is_success):
    percent = (current / total * 100) if total else 100
    status = "OK" if is_success else "SKIP"
    print(
        f"[Extract] Page {page} ({current}/{total}, {percent:.1f}%) "
        f"- {status}, total rows: {collected_rows}"
    )


def main():
    print("[1/3] Scraping product pages...")
    raw_product_data = scrape_data(
        DEFAULT_BASE_URL,
        progress_callback=_print_scrape_progress,
    )
    print(f"[1/3] Done. Collected {len(raw_product_data)} raw rows.")

    print("[2/3] Transforming data...")
    product_data = transform_data(raw_product_data)
    print(f"[2/3] Done. {len(product_data)} clean rows ready.")

    if not product_data.empty:
        print("[3/3] Saving CSV...")
        is_saved = save_to_csv(product_data, "products.csv")
        if is_saved:
            print("[3/3] Done. Data saved to products.csv")
        else:
            print("[3/3] Failed to save products.csv")

        print("[3/3] Saving Google Sheets...")
        spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
        spreadsheet_name = os.getenv("GOOGLE_SHEET_NAME")
        worksheet_name = os.getenv("GOOGLE_WORKSHEET_NAME", "Sheet1")
        credential_path = os.getenv("GOOGLE_SHEETS_CREDENTIAL_PATH", "google-sheets-api.json")
        is_saved_to_sheets = save_to_google_sheets(
            product_data,
            spreadsheet_id=spreadsheet_id,
            spreadsheet_name=spreadsheet_name,
            worksheet_name=worksheet_name,
            credential_path=credential_path,
        )
        if is_saved_to_sheets:
            print("[3/3] Done. Data saved to Google Sheets")
        else:
            print("[3/3] Skip/failed saving to Google Sheets. Check logs for details.")

        print(product_data)
    else:
        print("No data found.")


if __name__ == "__main__":
    main()
