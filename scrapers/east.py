from dataclasses import dataclass
from urllib.parse import urljoin
from datetime import datetime, timedelta

import httpx
from bs4 import BeautifulSoup

from my_funcs import insert_sequence, delete_sequence

from app import BaseUrl, Vendor
import re

storename = "East Ridge Lights"


@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:
    products = soup.find_all("div", class_="grid-product")
    sequences = []
    for product in products:
        sequence_name = product.find("a", class_="grid-product__title").text.strip()
        product_url = product.find("a", class_="grid-product__title")["href"]
        price = product.find("div", class_="grid-product__price-amount").text
        sequences.append(Sequence(sequence_name, product_url, price))

    return sequences


def main() -> None:
    print(f"Loading %s" % storename)
    baseurls = (
        BaseUrl.query.join(Vendor)
        .add_columns(Vendor.name.label("vendor_name"))
        .filter(Vendor.name == storename)
        .order_by(BaseUrl.id)
        .all()
    )
    for baseurl in baseurls:
        print(f"Loading %s" % baseurl[0].url)
        response = httpx.get(baseurl[0].url)
        soup = BeautifulSoup(response.text, "html.parser")
        products = get_products_from_page(soup, baseurl[0].url)

        for product in products:
            insert_sequence(
                store=storename, url=product.url, name=product.name, price=product.price
            )


if __name__ == "__main__":
    main()
