import pandas as pd
from utils.extract import scrape_data


def main():
    url = 'https://fashion-studio.dicoding.dev/'
    product_data = scrape_data(url)

    if product_data:
        df = pd.DataFrame(product_data)
        print(df)
    else:
        print("No data found.")


if __name__ == "__main__":
    main()
