from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

BASEURL = "https://shop.cfolights.com/product-category/sequences/"


@dataclass
class Sequence:
    name: str
    url: str


def get_products_from_page(soup: BeautifulSoup) -> list[Sequence]:

    products = soup.find_all("li", class_="type-product")

    sequences = []
    for product in products:
        sequence_name = product.find(class_="woocommerce-loop-product__title").text
        # song, artist = sequence_name.split(" - ")
        product_url = urljoin(BASEURL, product.find("a")["href"])
        sequences.append(Sequence(sequence_name, product_url))

    next_page = soup.find(class_="next")
    if next_page:
        response = httpx.get(next_page["href"])  # type: ignore
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.append(get_products_from_page(next_soup))

    return sequences


def main() -> None:

    response = httpx.get(BASEURL)
    soup = BeautifulSoup(response.text, "html.parser")
    products = get_products_from_page(soup)

    print(products)


if __name__ == "__main__":
    main()
