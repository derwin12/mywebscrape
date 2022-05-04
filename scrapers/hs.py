import re

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "Holiday Sequences"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all("div", class_="v-product")

    sequences = []
    for product in products:
        s = product.find("a", class_="v-product__title").text.strip()
        pattern = r"[^A-Za-z0-9\-\'\.()&]+"
        sequence_name = re.sub(pattern, " ", s).strip()
        product_url = product.find("a")["href"]
        price_text = product.find("div", class_="product_productprice").text
        pattern = re.compile(r"(\$\d[\d,.]*)")
        price = pattern.search(price_text)[1]  # type: ignore

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
