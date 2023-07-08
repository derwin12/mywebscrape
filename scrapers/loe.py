from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "LOE Sequences"


def get_products_from_page(
        soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all("li", class_="product")
    print(">>>>", products)
    sequences = []
    for product in products:
        sequence_name = product.find(class_="woocommerce-loop-product__title").text.strip()
        if any(x in sequence_name.lower() for x in ["pre-buy", "custom"]):
            print('Skip', sequence_name)
            continue
        product_url = urljoin(url, product.find("a")["href"])
        if any(x in product_url.lower() for x in ["pre-buy", "custom"]):
            continue
        price_float = min(
            float(x.text.strip().replace("$", ""))
            for x in product.find_all(class_="amount")
        )
        price = f"${price_float:.2f}"
        if price == "$0.00":
            price = "Free"

        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    next_tag = soup.find(class_="page-numbers")
    if next_tag:
        next_page = soup.find(class_="page-numbers").find(class_="next page-numbers")
        if next_page:
            response = httpx.get(next_page["href"], timeout=30.0)  # type: ignore
            next_soup = BeautifulSoup(response.text, "html.parser")
            sequences.extend(
                get_products_from_page(soup=next_soup, url=url, vendor=vendor)
            )

    return sequences


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    for url in vendor.urls:
        print(f"Loading {url.url}")
        response = httpx.get(url.url, timeout=30.0, follow_redirects=True)
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
