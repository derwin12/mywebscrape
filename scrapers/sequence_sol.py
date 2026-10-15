import time

import httpx
from bs4 import BeautifulSoup

from app import Sequence, Vendor
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "Sequence Solutions"


def get_with_retries(url: str, *, retries: int = 5, **kwargs) -> httpx.Response:
    # The site intermittently returns HTTP 500 for valid pages.
    for attempt in range(1, retries + 1):
        try:
            response = httpx.get(url, timeout=30.0, follow_redirects=True, **kwargs)
            if response.status_code < 500:
                return response
            error = f"HTTP {response.status_code}"
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            error = repr(exc)
        if attempt == retries:
            print(f"WARNING: giving up on {url} after {retries} attempts ({error}); items may be missing")
            return response if "response" in locals() else None
        print(f"  {url} failed ({error}), retrying (attempt {attempt}/{retries})")
        time.sleep(2 * attempt)


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all("div", class_="edd_download item")
    sequences = []
    for product in products:
        sequence_name = product.find("a", itemprop="url").text
        product_url = product.find("a", itemprop="url")["href"]
        price = product.find("span", class_="edd_price").text
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    if next_page := soup.find(class_="next"):
        response = get_with_retries(next_page["href"])  # type: ignore
        if response is None:
            return sequences
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.extend(get_products_from_page(soup=next_soup, url=url, vendor=vendor))

    return sequences


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    for url in vendor.urls:
        print(f"Loading {url.url}")
        response = get_with_retries(url.url)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
