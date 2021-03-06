import re
from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "Sequence Depot"


def get_product_price(url: str) -> str:
    response = httpx.get(url, timeout=30.0)
    soup = BeautifulSoup(response.text, "html.parser")
    prices = soup.find_all(class_="price")
    price_foat = min(float(x.text.strip().replace("$", "")) for x in prices)
    return f"${price_foat:.2f}"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    p = soup.find("div", class_="subcategories")
    products = p.find_all("li")  # type: ignore
    sequences = []
    # TODO: need to drill in for pricing
    price = get_product_price(url)
    for product in products:
        s = product.find(class_="name").text.strip()
        sequence_name = re.sub(r"[^A-Za-z0-9\-\'\.()&]+", " ", s).strip()
        product_url = urljoin(url, product.find("a")["href"])
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

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
