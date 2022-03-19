from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

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
        sequences.append(get_products_from_page(next_soup))

    return sequences


def main() -> None:

    products = []
    for url in BASEURLS:
        response = httpx.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        products.extend(get_products_from_page(soup))

    print(products)


if __name__ == "__main__":
    main()
