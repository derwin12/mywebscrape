from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

from insertData import insSequence

BASEURLS = [
    "https://sequencesol.com/christmas-sequences/",
    "https://sequencesol.com/halloween-sequences/",
    "https://sequencesol.com/other-sequences/",
]


@dataclass
class Sequence:
    name: str
    url: str


def get_products_from_page(soup: BeautifulSoup) -> list[Sequence]:

    products = soup.find_all("div", class_="edd_download item")

    sequences = []
    for product in products:
        sequence_name = product.find("a", itemprop="url").text
        product_url = product.find("a", itemprop="url")["href"]
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
        insSequence(store="Bostik", url=product.url, name=product.name)


if __name__ == "__main__":
    main()
