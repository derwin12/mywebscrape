import re
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from app import Vendor
from bs4 import BeautifulSoup
from my_funcs import get_unique_vendor, insert_sequence

storename = "Sequence Outlet"


@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:

    products = soup.find_all("div", class_="card--standard")
    sequences = []
    for product in products:
        sequence_name = product.find("h3").text.strip()
        product_url = urljoin(url, product.find("a")["href"])
        price_str = product.find("span", class_="price-item--sale").text.strip()
        price = "$" + re.sub(r"[^0-9\.]", "", price_str)
        if price == "$0.00":
            price = "Free"

        sequences.append(Sequence(sequence_name, product_url, price))

    return sequences


def main() -> None:
    print(f"Loading %s" % storename)
    vendor = get_unique_vendor(storename)

    for baseurl in vendor.urls:
        print(f"Loading %s" % baseurl.url)
        response = httpx.get(baseurl.url, follow_redirects=True)
        soup = BeautifulSoup(response.text, "html.parser")
        products = get_products_from_page(soup, baseurl.url)

        for product in products:
            insert_sequence(
                store=storename, url=product.url, name=product.name, price=product.price
            )


if __name__ == "__main__":
    main()
