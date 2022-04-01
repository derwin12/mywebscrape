import re
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from my_funcs import insert_sequence

from app import BaseUrl, Vendor

storename = 'BlinkySequences'


@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:
    results = soup.find(id="content")
    products = results.find_all("li", class_="product")
    sequences = []
    for product in products:
        s = product.find("h2").text.strip()
        pattern = r'[^A-Za-z0-9\-\'\.()&]+'
        sequence_name = re.sub(pattern, ' ', s).strip()
        # song, artist = sequence_name.split(" - ")
        product_url = product.find("a", class_="woocommerce-LoopProduct-link").attrs["href"]
        price = product.find("bdi").text
        if price == "$0.00":
            price = "Free"
        sequences.append(Sequence(sequence_name, product_url, price))

    return sequences

def main() -> None:
    print("Loading %s" % storename)
    baseurls = BaseUrl.query.join(Vendor).add_columns(Vendor.name.label("vendor_name")) \
        .filter(Vendor.name == storename).order_by(BaseUrl.id).all()
    for baseurl in baseurls:
        print(f"Loading %s" % baseurl[0].url)
        try:
            response = httpx.get(baseurl[0].url,timeout=10.0)
        except TimeoutError:
            print("WARNING: Unable to read website")
            pass
        if response:
            soup = BeautifulSoup(response.text, "html.parser")
            products = get_products_from_page(soup, baseurl[0].url)

            for product in products:
                insert_sequence(store=storename, url=product.url, name=product.name, price=product.price)


if __name__ == "__main__":
    main()
