from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from my_funcs import insert_sequence
import re
from app import Vendor

storename = "Sequence Outlet"


@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_product_info(url: str) -> tuple[str, str]:
    response = httpx.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    trs = soup.find_all("tr")
    name = trs[2].find_all("b")[1].text.strip()
    name = re.sub(r"\W\W+", " ", name)
    if "free" in name.lower():
        name = name.split()[0]
        price = "Free"
    else:
        price = trs[4].find_all("font")[0].text.split()[1]
    if price == "$0.00":
        price = "Free"

    return name, price


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:
    product_table = soup.find_all("table")[1]
    tds = product_table.find_all("td")
    products = [x for x in tds if x.text.strip()][:-1]

    sequences = []
    for product in products:
        product_url = urljoin(url, product.find("a")["href"])
        sequence_name, price = get_product_info(product_url)
        sequences.append(Sequence(sequence_name, product_url, price))

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
