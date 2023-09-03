import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "Flash The Neighbors"


def get_products_from_page(
    soup: BeautifulSoup, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all(class_="grid-product")
    sequences = []
    for product in products:
        sequence_name = product.find(
            class_="grid-product__title-inner"
        ).text.strip()
        product_url = product.find("a", class_="grid-product__title")["href"]
        price = product.find(class_="grid-product__price-value").text.strip()
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
        print(f"Loading {url.url}")
        response = httpx.get(url.url, timeout=30.0)
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
