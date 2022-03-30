import re
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from my_funcs import insert_sequence

from app import BaseUrl, Vendor

storename = 'Animated Illumination'


@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:
    products = soup.find_all("div", class_="edd_download_inner")
    sequences = []
    for product in products:
        s = product.find(class_="edd_download_title").text
        pattern = r'[^A-Za-z0-9\-\'\.()&]+'
        sequence_name = re.sub(pattern, ' ', s).strip()
        # song, artist = sequence_name.split(" - ")
        product_url = urljoin(url, product.find("a")["href"])
        if product.find("div", class_="edd_price_options"):
            p_text = product.find("div", class_="edd_price_options")

            p_text2 = p_text.find("input")["data-price"]
            if p_text2:
                price = p_text.find("input")["data-price"]
            else:
                price = "-"
        else:
            p_text = product.find("a", class_="edd-add-to-cart")
            if p_text:
                price = p_text["data-price"]
            else:
                price = "Free"
        sequences.append(Sequence(sequence_name, product_url, price))

    return sequences


def main() -> None:
    print(f"Loading %s" % storename)
    baseurls = BaseUrl.query.join(Vendor).add_columns(Vendor.name.label("vendor_name")) \
        .filter(Vendor.name == storename).order_by(BaseUrl.id).all()
    for baseurl in baseurls:
        # Using page saved since I was flagged as robot
        response = open("C:\\Users\\elcrapamundo\\PycharmProjects\\webscrape\\app\\Sample-Animated Illumination.html")
        print(f"Loading %s" % baseurl[0].url)
        soup = BeautifulSoup(response, "html.parser")
        products = get_products_from_page(soup, baseurl[0].url)

        for product in products:
            insert_sequence(store=storename, url=product.url, name=product.name, price=product.price)


if __name__ == "__main__":
    main()
