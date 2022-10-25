import re
import os

from bs4 import BeautifulSoup
from app import Sequence, Vendor

from my_funcs import create_or_update_sequences, get_unique_vendor

from pathlib import Path

storename = "Music with Motion"
BASEURL = 'https://musicwithmotion.com/'
FileDir = "MusicWithMotion"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all("div", class_="product-layout")
    sequences = []
    for product in products:
        sequence_name = product.find("h4").text
        product_url = product.find("a")["href"]
        p = product.find("p", class_="price").text
        # <p class="price">$35.00 <span class="price-tax">Ex Tax:$35.00</span>
        pattern = r"[^0-9\.\$]+"
        pt = re.sub(pattern, " ", p).strip()
        price = pt.split(" ")[0].lstrip(' ')

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

    if os.name != 'posix':
        htmldir = os.getcwd() + "\\..\\app\\Data\\" + FileDir
    else:
        htmldir = os.getcwd() + "//app//Data//" + FileDir
    for p in Path(htmldir).glob('*.html'):
        print(f"Loading %s" % (p.name.split('.')[0]))
        with p.open() as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")
        sequences = get_products_from_page(soup=soup, url=BASEURL + "\\" + p.name, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
