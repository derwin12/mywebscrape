import re
from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "BF Light Shows"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all("li", class_="grid__item")

    sequences = []
    for product in products:
        name_tag = product.find("h3", class_="card__heading")
        if not name_tag:
            continue
        link_tag = name_tag.find("a", class_="full-unstyled-link")
        if not link_tag:
            continue
        sequence_name = link_tag.text.strip()
        if any(x in sequence_name.lower() for x in ["rgb sequence", "services", "voice over"]):
            continue
        print(sequence_name)
        product_url = urljoin(url, link_tag["href"])

        # Extract price
        price_container = product.find("div", class_="price__sale")
        if not price_container:
            continue
        price_tag = price_container.find("span", class_="price-item price-item--sale price-item--last")
        if not price_tag:
            continue
        price_text = price_tag.text.strip()

        # Extract price using regex to handle formats like "From $36.00 CAD"
        prices = re.findall(r"\$([0-9\.]+)", price_text)
        price = prices[0] if prices else "0"
        price = f"${price}"
        if price == "$0.00":
            price = "Free"

        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    # Handle pagination
    next_page_link = soup.find("a", class_="pagination__item pagination__item--prev pagination__item-arrow link motion-reduce")
    if next_page_link:
            next_page_url = urljoin(url, next_page_link["href"])
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
