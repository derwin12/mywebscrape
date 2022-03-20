from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from insertData import insSequence

BASEURL = "https://visionarylightshows.com/collections/all"


@dataclass
class Sequence:
    name: str
    url: str


def get_products_from_page(soup: BeautifulSoup) -> list[Sequence]:

    products = soup.find_all("div", class_="product-card")

    sequences = []
    for product in products:
        sequence_name = product.find("a").text.strip()
        product_url = urljoin(BASEURL, product.find("a")["href"])
        sequences.append(Sequence(sequence_name, product_url))

    next_page = soup.find("ul", "list--inline pagination").find_all("li")[-1].find("a")
    if next_page:
        response = httpx.get(urljoin(BASEURL, next_page["href"]))  # type: ignore
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.extend(get_products_from_page(next_soup))

    return sequences


def main() -> None:

    response = httpx.get(BASEURL)
    soup = BeautifulSoup(response.text, "html.parser")
    products = get_products_from_page(soup)

    for product in products:
        insSequence(store="Bostik", url=product.url, name=product.name)


if __name__ == "__main__":
    main()
