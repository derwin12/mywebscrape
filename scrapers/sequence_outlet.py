import re
from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "Sequence Outlet"


def get_products_from_page(
        soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all("div", class_="card--standard")
    sequences = []
    for product in products:
        sequence_name = product.find("h3").text.strip()
        product_url = urljoin(url, product.find("a")["href"])
        price_str = product.find("span", class_="price-item--sale").text.strip()
        price = "$" + re.sub(r"[^0-9.]", "", price_str)
        if price == "$0.00":
            price = "Free"

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
