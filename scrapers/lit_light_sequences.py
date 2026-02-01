from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "Lit Light Sequences"


def get_minimum_price(price_soup: list[BeautifulSoup]) -> str:
    price_strs = [x.text.strip() for x in price_soup]
    price_floats = [
        float(price_str.split()[0].replace("$", "").strip())
        for price_str in price_strs
        if "USD" in price_str
    ]

    return f"${min(price_floats):.2f}"


def get_products_from_page(
        soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all(class_="card-wrapper")
    sequences = []
    for product in products:
        sequence_name = product.find(class_="full-unstyled-link").text.strip()
        product_url = urljoin(url, product.find("a")["href"])
        prices_soup = product.find_all(class_="price-item")
        price = get_minimum_price(prices_soup)

        if price == "$0.00":
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
        page_num = 1
        while True:
            # Construct page URL
            if page_num == 1:
                page_url = url.url
            else:
                page_url = f"{url.url}?page={page_num}"

            print(f"Loading {page_url}")
            response = httpx.get(page_url, timeout=30.0)
            soup = BeautifulSoup(response.text, "html.parser")
            sequences = get_products_from_page(soup=soup, url=page_url, vendor=vendor)

            create_or_update_sequences(sequences)

            # Check if there's a next page
            # Look for pagination links - typically in a nav or pagination element
            pagination = soup.find_all("a", href=True)
            next_page_exists = False

            for link in pagination:
                href = link.get("href", "")
                if f"page={page_num + 1}" in href:
                    next_page_exists = True
                    break

            if next_page_exists:
                page_num += 1
            else:
                print(f"No more pages found after page {page_num}")
                break


if __name__ == "__main__":
    main()