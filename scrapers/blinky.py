import httpx
from app import Sequence
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "BlinkySequences"


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:
    products = soup.find_all(class_="product")
    sequences = []
    for product in products:
        sequence_name = product.find(
            class_="woocommerce-loop-product__title"
        ).text.strip()
        product_url = product.find("a", class_="woocommerce-LoopProduct-link")["href"]
        price = product.find(class_="price").text
        if price == "$0.00":
            price = "Free"
        sequences.append(Sequence(name=sequence_name, link=product_url, price=price))

    return sequences


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    for url in vendor.urls:
        print(f"Loading {url.url}")
        response = httpx.get(url.url)
        soup = BeautifulSoup(response.text, "html.parser")
        products = get_products_from_page(soup, url.url)

        create_or_update_sequences(products)


if __name__ == "__main__":
    main()
