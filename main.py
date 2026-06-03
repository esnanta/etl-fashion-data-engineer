from utils.extract import scrape_data
from utils.transform import transform_data


def main():
    url = 'https://fashion-studio.dicoding.dev/'
    raw_product_data = scrape_data(url)
    product_data = transform_data(raw_product_data)

    if not product_data.empty:
        print(product_data)
    else:
        print("No data found.")


if __name__ == "__main__":
    main()
