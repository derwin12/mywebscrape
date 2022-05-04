import re

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "OG Sequences"


def get_price_from_product_page(product_url: str) -> str:
    response = httpx.get(product_url, follow_redirects=True, timeout=30.0)
    soup = BeautifulSoup(response.text, "html.parser")

    prices = soup.find_all("meta", itemprop="price")
    price = max(float(i["content"]) for i in prices)
    return f"${price:.2f}"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all("div", class_="elementor-image")

    sequences = []
    for product in products:
        sequence_name = product.text.replace("*", "").strip()
        product_url = product.find("a")["href"]

        if "ogsequences" not in product_url:
            seq_num = re.search(".*p=(\d+).*", product_url)[1]  # type: ignore
            product_url = (
                f"http://ogsequences.com/?post_type=download&p={seq_num}&preview=true"
            )

        # Price is on a secondary page.
        price = get_price_from_product_page(product_url)
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    next_page = soup.find(class_="next")
    if next_page:
        print(f"Loading {next_page['href']}")  # type: ignore
        response = httpx.get(next_page["href"], timeout=30.0)  # type: ignore
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
