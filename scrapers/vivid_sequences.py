from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from my_funcs import insert_sequence

from app import Vendor

storename = "Vivid Sequences"


@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:
    products = soup.find_all("li", class_="type-product")
    sequences = []
    for product in products:
        sequence_name = product.find(
            class_="woocommerce-loop-product__title"
        ).text.strip()
        product_url = urljoin(url, product.find("a")["href"])
        price = product.find_all(class_="amount")[-1].text.strip()
        if price == "$0.00":
            price = "Free"
        sequences.append(Sequence(sequence_name, product_url, price))

    next_page = soup.find(class_="next")
    if next_page:
        response = httpx.get(next_page["href"])  # type: ignore
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.extend(get_products_from_page(next_soup, url))

    return sequences


def main() -> None:
    print(f"Loading %s" % storename)

    vendor = Vendor.query.filter_by(name=storename).all()
    if not vendor:
        raise Exception(f"{storename} not found in database.")
    elif len(vendor) > 1:
        raise Exception(f"{storename} found multiple times in database.")

    baseurls = vendor[0].urls
    for baseurl in baseurls:
        print(f"Loading %s" % baseurl.url)
        response = httpx.get(baseurl.url)
        soup = BeautifulSoup(response.text, "html.parser")
        products = get_products_from_page(soup, baseurl.url)

        for product in products:
            insert_sequence(
                store=storename, url=product.url, name=product.name, price=product.price
            )


if __name__ == "__main__":
    main()
