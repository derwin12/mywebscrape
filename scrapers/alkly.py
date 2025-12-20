from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor
import re

storename = "Alkly Designs"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all('li', class_='grid__item scroll-trigger animate--slide-in')
    sequences = []
    for product in products:
        sequence_name = product.find("a").text.strip().replace(" - xLights Sequence", "")
        product_url = urljoin(url, product.find("a")["href"])

        if price_sale := product.find(class_="price-item--sale"):
            price_string = price_sale.text.strip()
        else:
            price_string = product.find(class_="price-item--regular").text.strip()

        match = re.search(r"\$\d+\.\d{2}", price_string)
        price = match.group()

        if price == "$0.00":
            price = "Free"

        print(product_url, price)
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    return sequences


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    for url in vendor.urls:
        print(f"Loading {url.url}")
        response = httpx.get(url.url, timeout=30.0)
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
