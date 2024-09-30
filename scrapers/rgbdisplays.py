import re
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app import Sequence, Vendor
from my_funcs import create_or_update_sequences, get_unique_vendor

# Might get the wrong country for pricing
storename = "RGB Displays"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all("li", class_="grid__item")
    sequences = []
    for product in products:
        sequence_name = product.find("h3").text.strip()
        product_url = urljoin(url, product.find("a")["href"])
        p_str = product.find("div", class_="price__container").text.strip()
        prices = re.findall(r".*[\$£]([0-9\.]+).*", p_str)
        price = prices[0] if len(prices) == 1 else str(min(prices))
        if "$" not in price:
            price = f"${price}"
        if price == "$0.00":
            price = "Free"
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )
    if next_page := soup.find_all('a', class_='pagination__item-arrow', attrs={'aria-label': 'Next page'}):
        last_href = next_page[-1].get('href')
        response = httpx.get(urljoin(url,last_href), timeout=30.0)  # type: ignore
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.extend(get_products_from_page(soup=next_soup, url=url, vendor=vendor))

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
