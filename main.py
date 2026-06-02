import requests
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}


def extract_data(section):
    tempat_wisata = section.find('h3').text
    deskripsi = section.find('p').text.replace('\n', '').strip()
    url_gambar = section.find('img')["src"]

    return {
        "tempat_wisata": tempat_wisata,
        "deskripsi": deskripsi,
        "url_gambar": url_gambar
    }


def fetch_page(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error saat mengambil {url}: {e}")
        return None


def scrape_data(url):
    content = fetch_page(url)
    if not content:
        return []

    soup = BeautifulSoup(content, 'html.parser')
    data = []
    articles = soup.find('article', id='wisata', class_='card')

    if articles:
        sections = [desc for desc in articles.descendants if desc.name == 'section']
        for section in sections:
            tourism_data = extract_data(section)
            data.append(tourism_data)
    return data


def main():
    url = 'https://fashion-studio.dicoding.dev/'
    tourism_data = scrape_data(url)

    if tourism_data:
        df = pd.DataFrame(tourism_data)
        print(df)
    else:
        print("Tidak ada data yang ditemukan.")


if __name__ == "__main__":
    main()
