from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor
import re

storename = "Easy xLights Sequences"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all('li', class_='ast-grid-common-col')
    sequences = []
    for product in products:
        sequence_name = product.find("h2", class_='woocommerce-loop-product__title').text
        product_url = urljoin(url, product.find("a")["href"])

        price_string = product.find(class_="woocommerce-Price-amount").text.strip()

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

    next_page = soup.find(class_="next")
    if next_page:
        print(f'Loading {urljoin(url, next_page["href"])}')  # type: ignore
        try:
            response = httpx.get(next_page["href"], timeout=90.0)  # type: ignore
            next_soup = BeautifulSoup(response.text, "html.parser")
            sequences.extend(get_products_from_page(soup=next_soup, url=url, vendor=vendor))
        except Exception as e:
            print(f"Timed out. Lets just continue on")

    return sequences


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    for url in vendor.urls:
        print(f"Loading {url.url}")
        response = httpx.get(url.url, timeout=90.0)
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
