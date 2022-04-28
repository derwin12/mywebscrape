import os
import re
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

from my_funcs import insert_sequence

from pathlib import Path

storename = 'Music with Motion'
BASEURL = 'https://musicwithmotion.com/'
FileDir = "MusicWithMotion"

@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:
    products = soup.find_all("div", class_="product-layout")
    sequences = []
    for product in products:
        sequence_name = product.find("h4").text
        # song, artist = sequence_name.split(" - ")
        product_url = product.find("a")["href"]
        p = product.find("p", class_="price").text
        pattern = r'[^0-9\.\$]+'
        price_text = re.sub(pattern, ' ', p).strip()
        pattern = re.compile("(\$[0-9]+).*(\$[0-9]+)")
        try:
            price = pattern.search(price_text)[2]
        except:
            price = price_text
        if price == "$0":
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
    if os.name != "posix":
        htmldir = os.getcwd() + "\\..\\app\\Data\\" + FileDir
    else:
        htmldir = os.getcwd() + "//app//Data//" + FileDir
    for p in Path(htmldir).glob('*.html'):
        print(f"Loading %s" % (p.name.split('.')[0]))
        with p.open() as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")
        products = get_products_from_page(soup, BASEURL + "\\" + p.name)

        for product in products:
            insert_sequence(store=storename, url=product.url, name=product.name, price=product.price)


if __name__ == "__main__":
    main()
