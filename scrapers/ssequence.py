from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from my_funcs import insert_sequence

from app import BaseUrl, Vendor
import re

storename = 'Show Sequences'


@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:
    products = soup.find_all("li", attrs={"class": re.compile('product type-product')})
    sequences = []
    for product in products:
        s = product.find("h3").text.strip()
        pattern = r'[^A-Za-z0-9\-\'\.()&]+'
        sequence_name = re.sub(pattern, ' ', s).strip()
        product_url = urljoin(url, product.find("a")["href"])
        p = product.find("span", class_="price").text
        pattern = r'[^0-9\.\$]+'
        price_text = re.sub(pattern, ' ', p).strip()
        pattern = re.compile("(\$[0-9]+).*(\$[0-9]+)")
        try:
            price = pattern.search(price_text)[2]
        except:
            price = price_text
        if price == "$0":
            price = "Free"
            print("price", price)
        sequences.append(Sequence(sequence_name, product_url, price))

    next_tag = soup.find(class_="NOTUSED")
    if next_tag:
        np = next_tag.find("a")
        if np:
            next_page = urljoin(url, np["href"])
            print(f"Loading %s" % (next_page))
            response = httpx.get(next_page)  # type: ignore
            next_soup = BeautifulSoup(response.text, "html.parser")
            sequences.extend(get_products_from_page(next_soup, url))

    return sequences


def main() -> None:
    print(f"Loading %s" % storename)
    baseurls = BaseUrl.query.join(Vendor).add_columns(Vendor.name.label("vendor_name")) \
        .filter(Vendor.name == storename).order_by(BaseUrl.id).all()
    for baseurl in baseurls:
        print(f"Loading %s" % baseurl[0].url)
        try:
            response = httpx.get(baseurl[0].url, timeout=15)
        except Exception as ex:
            print("Exception", ex.args)
            continue
        soup = BeautifulSoup(response.text, "html.parser")
        products = get_products_from_page(soup, baseurl[0].url)

        for product in products:
            insert_sequence(store=storename, url=product.url, name=product.name, price=product.price)


if __name__ == "__main__":
    main()
