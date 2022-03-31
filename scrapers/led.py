from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from my_funcs import insert_sequence

from app import BaseUrl, Vendor
import re

storename = 'LED Warehouse'


@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:
    products = soup.find_all("div", class_="boost-pfs-filter-product-item-inner")

    sequences = []
    for product in products:
        s = product.find("a", class_="boost-pfs-filter-product-item-title").text.strip()
        pattern = r'[^A-Za-z0-9\-\'\.()&]+'
        sequence_name = re.sub(pattern, ' ', s).strip()
        product_url = urljoin(url, product.find("a")["href"])
        price_text = product.find("p", class_="boost-pfs-filter-product-item-price").text
        pattern = re.compile(r'(\$\d[\d,.]*)')
        price = pattern.search(price_text).group(1)
        sequences.append(Sequence(sequence_name, product_url, price))

    next_page = soup.find("link", attrs={"rel": "next"})
    if next_page:
        response = httpx.get(urljoin(url, next_page["href"]))  # type: ignore
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.extend(get_products_from_page(next_soup, url))

    return sequences


def main() -> None:
    print(f"Loading %s" % storename)
    baseurls = BaseUrl.query.join(Vendor).add_columns(Vendor.name.label("vendor_name")) \
        .filter(Vendor.name == storename).order_by(BaseUrl.id).all()
    for baseurl in baseurls:
        print(f"Loading %s" % baseurl[0].url)
        response = httpx.get(baseurl[0].url)
        soup = BeautifulSoup(response.text, "html.parser")
        products = get_products_from_page(soup, baseurl[0].url)

        for product in products:
            insert_sequence(store=storename, url=product.url, name=product.name, price=product.price)


if __name__ == "__main__":
    main()
