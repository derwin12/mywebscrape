from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "HolidayCoro"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all("div", class_="v-product")
    sequences = []
    for product in products:
        sequence_name = product.find("a", class_="v-product__title").text.strip()
        product_url = urljoin(url, product.find("a")["href"])
        price = (
            product.find("div", class_="product_productprice")
            .text.split(":")[-1]
            .strip()
        )
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

        # I added this directly to my BaseUrl table as it eliminates the need for a pager
        if not url.url.endswith("300"):
            url.url = f"{url.url}?searching=Y&show=300"
        print(f"Loading {url.url}")
        response = httpx.get(url.url)
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
