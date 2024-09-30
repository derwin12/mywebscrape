from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app import Sequence, Vendor
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "Innovative Sequences"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all("li", class_="grid__item")

    sequences = []
    for product in products:
        sequence_name = product.find("h3").text.strip()
        product_url = urljoin(url, product.find("a")["href"])
        if price_sale := product.find(class_="price-item--sale"):
            price = price_sale.text.strip()
        else:
            price = product.find(class_="price-item--regular").text.strip()
        if price == "$0":
            price = "Free"
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    if (
        next_page := soup.find("ul", "pagination__list list-unstyled")
        .find_all("li")[-1]
        .find("a")
    ):
        response = httpx.get(urljoin(url, next_page["href"]), timeout=30.0)  # type: ignore
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.extend(get_products_from_page(soup=next_soup, url=url, vendor=vendor))

    return sequences


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    for url in vendor.urls:
        print(f"Loading {url.url}")
        response = httpx.get(url.url, timeout=30.0)
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
