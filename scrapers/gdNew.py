import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timedelta, date

from my_funcs import insert_sequence, delete_sequence

import httpx
from bs4 import BeautifulSoup


SHARED_LINK = "https://drive.google.com/drive/folders/0B2ozCEidtWh3ZURlVWFvenRiSVk" + \
                "?resourcekey=0-t4zYmi-whU6yaxp08BQfSw&usp=sharing"
storename = 'GoogleDrive'


@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_products_from_page(shared_link: str) -> list[Sequence]:
    sequences = []

    response = httpx.get(shared_link)
    soup = BeautifulSoup(response.text, "html.parser")
    files = soup.find_all("div", role="gridcell")

    for file in files:
        file_name = file.find("div", attrs={"data-tooltip-unhoverable": "true"})
        url_link = file.find("img")
        if url_link:
            if file_name.text.endswith("zip") or file_name.text.endswith("piz"):
                sequence_name = "[_NEW] " + file_name.text.split(".")[0]
                product_url = SHARED_LINK + "&" + \
                    urllib.parse.quote(file_name.text.split(".")[0])
                price = "Free"
                sequences.append(Sequence(sequence_name, product_url, price))

    return sequences


def main() -> None:
    print(f"Loading %s" % storename)
    products = get_products_from_page(SHARED_LINK)

    for product in products:
        insert_sequence(store=storename, url=product.url, name=product.name, price=product.price)

    if products:
        delete_sequence(store=storename, name = '[_NEW]', last_upd=(datetime.now() - timedelta(days=14)))


if __name__ == "__main__":
    main()
