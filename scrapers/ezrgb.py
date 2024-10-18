import re
from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "EZRGB"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all("li", class_="product")
    sequences = []
    pattern = r"[^A-Za-z0-9\-\'\.()&]+"
    for product in products:
        s = product.find("h3").text.strip()
        s2 = re.sub(pattern, " ", s).strip()
        sequence_name = re.sub(r'\(.*?\)', '', s2).strip()
        # song, artist = sequence_name.split(" - ")
        product_url = urljoin(url, product.find("a")["href"])
        if product.find("bdi"):
            price = product.find("bdi").text
        else:
            price = "Unknown"
        print(sequence_name, product_url, price)
        if price == "$0.00":
            price = "Free"
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    next_page = soup.find("link", attrs={"rel": "next"})
    if next_page:
        print(f'Loading {urljoin(url, next_page["href"])}')  # type: ignore
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
