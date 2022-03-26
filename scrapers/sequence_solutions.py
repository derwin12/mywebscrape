from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

from my_funcs import insert_sequence

from app import BaseUrl, Vendor

storename = 'SequenceSol'


@dataclass
class Sequence:
    name: str
    url: str


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:

    products = soup.find_all("div", class_="edd_download item")

    sequences = []
    for product in products:
        sequence_name = product.find("a", itemprop="url").text
        product_url = product.find("a", itemprop="url")["href"]
        sequences.append(Sequence(sequence_name, product_url))

    next_page = soup.find(class_="next")
    if next_page:
        response = httpx.get(next_page["href"])  # type: ignore
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.extend(get_products_from_page(next_soup, url))

    return sequences


def main() -> None:
    products = []

    baseurls = BaseUrl.query.join(Vendor).add_columns(Vendor.name.label("vendor_name")) \
        .filter(Vendor.name == storename).order_by(BaseUrl.id).all()
    for baseurl in baseurls:
        response = httpx.get(baseurl[0].url)
        soup = BeautifulSoup(response.text, "html.parser")
        products.extend(get_products_from_page(soup, baseurl[0].url))

    for product in products:
        insert_sequence(store=storename, url=product.url, name=product.name)


if __name__ == "__main__":
    main()
