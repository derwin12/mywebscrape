import re
from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "Whimsical Light Shows"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all("div", class_="wsite-com-category-product")
    sequences = []
    for product in products:
        s = product.find("div", class_="wsite-com-category-product-name").text.strip()
        pattern = r"[^A-Za-z0-9\-\'\.()&]+"
        sequence_name = re.sub(pattern, " ", s).strip()
        # song, artist = sequence_name.split(" - ")
        product_url = urljoin(url, product.find("a")["href"])
        p = product.find("div", class_="wsite-com-product-price").text
        pattern = r"[^0-9\.\$]+"
        price_text = re.sub(pattern, " ", p).strip()
        pattern = re.compile(r"(\$\d[\d.]+).*(\$\d[\d.]+)")
        try:
            price = pattern.search(price_text)[2]  # type: ignore
        except Exception:
            price = price_text
        if price == "$0":
            price = "Free"
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
        response = httpx.get(url.url)
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
