import re
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from my_funcs import insert_sequence

from app import BaseUrl, Vendor

storename = 'xLightsSequences'


@dataclass
class Sequence:
    name: str
    url: str


BASEURL = "https://showstoppersequences-com.3dcartstores.com/"


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:

    products = soup.find_all("div", class_="structItem")
    sequences = []
    for product in products:
        pattern = r'[^A-Za-z0-9\-\'\.()&]+'
        s = product.find("div", class_="structItem-title").find("a", attrs={"data-tp-primary": "on"}).text
        sequence_name = re.sub(pattern, ' ', s).strip()
        # song, artist = sequence_name.split(" - ")
        product_url = urljoin(url,
                              product.find("div",
                                     class_="structItem-title").find("a", attrs={"data-tp-primary": "on"})["href"])
        sequences.append(Sequence(sequence_name, product_url))

    next_page = soup.find(class_="pageNav-jump pageNav-jump--next")
    if next_page:
        next_page_url = urljoin(url, soup.find("a", class_="pageNav-jump pageNav-jump--next")["href"])  # type: ignore
        print(f"Loading %s" % next_page_url)
        response = httpx.get(next_page_url)
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.extend(get_products_from_page(next_soup, url))

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
            insert_sequence(store=storename, url=product.url, name=product.name)


if __name__ == "__main__":
    main()
