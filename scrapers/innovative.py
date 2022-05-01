from urllib.parse import urljoin

import httpx
from app import Sequence
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "Innovative Sequences"


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:
    products = soup.find_all("li", class_="grid__item")

    sequences = []
    for product in products:
        sequence_name = product.find("h3").text.strip()
        product_url = urljoin(url, product.find("a")["href"])
        if price_sale := product.find(class_="price-item--sale"):
            price = price_sale.text.strip()
        else:
            price = product.find(class_="price-item--regular").text.strip()
        if price == "$0":
            price = "Free"
        sequences.append(Sequence(name=sequence_name, link=product_url, price=price))

    return sequences


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    for url in vendor.urls:
        print(f"Loading {url.url}")
        response = httpx.get(url.url)
        soup = BeautifulSoup(response.text, "html.parser")
        products = get_products_from_page(soup, url.url)

        create_or_update_sequences(products)


if __name__ == "__main__":
    main()
