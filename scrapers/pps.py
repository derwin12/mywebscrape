import re
from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "PixelPerfectSequences"
BASEURL = "https://pixelperfectsequences.com"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all(
        "div", class_="grid__item small--one-half medium-up--one-fifth"
    )
    sequences = []
    for product in products:
        sequence_name = product.find(class_="product-card__name").text
        product_url = urljoin(BASEURL, product.find("a")["href"])
        p = product.find("div", class_="product-card__price").text
        pattern = r"[^\$0-9\.]+"
        price_text = re.sub(pattern, " ", p).strip()
        pattern = re.compile(r"(\$[0-9]+).*(\$[0-9]+)")  # Look for second price
        try:
            price = pattern.search(price_text)[2]  # type: ignore
        except Exception:
            price = price_text
        if price == "$0":
            price = "Free"
        sequences.append(
            Sequence(
                name=sequence_name,
                vendor_id=vendor.id,
                link=product_url,
                price=price,
            )
        )

    next_page = soup.find(class_="next")
    if next_page:
        next_page_url = urljoin(url, next_page.find("a")["href"])  # type: ignore
        response = httpx.get(next_page_url, timeout=30.0)
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
