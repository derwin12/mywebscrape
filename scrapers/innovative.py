from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from my_funcs import insert_sequence

from app import BaseUrl, Vendor
import re

storename = 'Innovative Sequences'
page = 1


@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:
    global page
    products = soup.find_all("li", class_="grid__item")

    sequences = []
    for product in products:
        s = product.find("h3").text.strip()
        pattern = r'[^A-Za-z0-9\-\'\.()&]+'
        sequence_name = re.sub(pattern, ' ', s).strip()
        # song, artist = sequence_name.split(" - ")
        product_url = urljoin(url, product.find("a")["href"])
        p_text = product.find("div", class_="price").text.strip()
        pattern = r'[^0-9\.\$]+'
        price_text = re.sub(pattern, ' ', p_text).strip()
        pattern = re.compile("(\$[0-9]+).*(\$[0-9]+)")
        try:
            price = pattern.search(price_text)[2]
        except TypeError:
            try:
                pattern = re.compile(".*(\$[0-9]+\.[0-9]+).*")
                price = pattern.search(p_text).group(1)
            except TypeError:
                price = "Free"
        if (price == "$0"):
            price = "Free"
        sequences.append(Sequence(sequence_name, product_url, price))


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