from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from my_funcs import insert_sequence

from app import BaseUrl, Vendor
import re

storename = "Electro Sequences"


@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:
    products = soup.find_all("div", class_="grid-view-item")
    sequences = []
    for product in products:
        sequence_name = product.find("div", class_="h4").text.strip()
        product_url = urljoin(url, product.find("a", class_="grid-view-item__link")["href"])
        p = product.find("div", class_="price__regular").text
        pattern = r'[^0-9\.\$]+'
        price_text = re.sub(pattern, ' ', p).strip()
        pattern = re.compile("(\$[0-9]+).*(\$[0-9]+)")
        try:
            price = pattern.search(price_text)[2]
        except TypeError:
            price = price_text
        if price == "$0":
            price = "Free"
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
