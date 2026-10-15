import re
from urllib.parse import urljoin

from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor, http_get

storename = "Microcyb"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    sequences = []
    for product in soup.find_all("div", class_="single-product-info"):
        link = product.find("h6").find("a")
        sequence_name = link.get("title") or link.text.strip()
        product_url = urljoin(url, link["href"].split("#")[0])

        price_element = product.find(class_="single-product-price")
        match = re.search(r"\$\d+\.\d{2}", price_element.text) if price_element else None
        price = match.group() if match else "Free"
        if price == "$0.00":
            price = "Free"

        print(product_url, price)
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
        page_url = url.url
        total_pages = 1
        page = 1
        while page <= total_pages:
            print(f"Loading {page_url} page {page}")
            response = http_get(
                page_url,
                params={"page": page} if page > 1 else None,
                timeout=60.0,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            soup = BeautifulSoup(response.text, "html.parser")
            if page == 1:
                grid = soup.find(id="shop-grid")
                total_pages = int(grid["data-total-pages"]) if grid else 1
            create_or_update_sequences(
                get_products_from_page(soup=soup, url=page_url, vendor=vendor)
            )
            page += 1


if __name__ == "__main__":
    main()
