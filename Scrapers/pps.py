from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from my_funcs import insSequence

BASEURLS = ["https://pixelperfectsequences.com/collections/christmas-2",
            "https://pixelperfectsequences.com/collections/halloween-sequences",
            ]

BASEURL = "https://pixelperfectsequences.com"


@dataclass
class Sequence:
    name: str
    url: str


def get_products_from_page(soup: BeautifulSoup) -> list[Sequence]:
    products = soup.find_all("div", class_="grid__item small--one-half medium-up--one-fifth")

    sequences = []
    for product in products:
        sequence_name = product.find(class_="product-card__name").text
        # song, artist = sequence_name.split(" - ")
        product_url = urljoin(BASEURL, product.find("a")["href"])
        sequences.append(Sequence(sequence_name, product_url))

    next_page = soup.find(class_="next")
    if next_page:
        response = httpx.get(next_page["href"])  # type: ignore
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.extend(get_products_from_page(next_soup))

    return sequences


def main() -> None:
    products = []
    for url in BASEURLS:
        response = httpx.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        products.extend(get_products_from_page(soup))

    for product in products:
        print(product.url, product.name)
        insSequence(store="PixelPerfectSequences", url=product.url, name=product.name)


if __name__ == "__main__":
    main()
