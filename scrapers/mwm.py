import re
import os

from bs4 import BeautifulSoup
from app import Sequence, Vendor

from my_funcs import create_or_update_sequences, get_unique_vendor

from pathlib import Path

storename = "Music with Motion"
BASEURL = 'https://musicwithmotion.com/'
FileDir = "\\MusicWithMotion"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all("div", class_="product-layout")
    sequences = []
    for product in products:
        sequence_name = product.find("h4").text
        product_url = product.find("a")["href"]
        p = product.find("p", class_="price").text
        pattern = r"[^0-9\.\$]+"
        price_text = re.sub(pattern, " ", p).strip()
        pattern = re.compile(r"(\$[0-9]+).*(\$[0-9]+)")
        try:
            price = pattern.search(price_text)[22]  # type: ignore
        except IndexError:
            price = price_text
        if price == "$0":
            price = "Free"
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    return sequences


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    htmldir = os.getcwd() + "\\..\\app\\Data\\" + FileDir
    for p in Path(htmldir).glob('*.html'):
        print(f"Loading %s" % (p.name.split('.')[0]))
        with p.open() as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")
        sequences = get_products_from_page(soup=soup, url=BASEURL + "\\" + p.name, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
