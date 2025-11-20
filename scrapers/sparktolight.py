import httpx, re
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "Spark To Light"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all("div",  class_='card-wrapper product-card-wrapper underline-links-hover')

    page_links = soup.find_all("a", href=re.compile(r"page=", re.I))
    next_page = None
    for link in page_links:
        text = link.get_text(strip=True)
        if "next" in text.lower():
            next_page = link
            break

    sequences = []
    for product in products:
        sequence_name = product.find('h3', class_='card__heading font-section-collection-productName builder-pointer-events-all-in-color-tweaks-manager').get_text(strip=True)
        product_url = product.find('h3', class_='card__heading font-section-collection-productName builder-pointer-events-all-in-color-tweaks-manager').find('a')['href']
        price = "Unknown"
        if product_url:
            response = httpx.get(product_url, timeout=30.0, follow_redirects=True)
            if response.status_code == 200:
                product_soup = BeautifulSoup(response.text, "html.parser")
                price_divs = product_soup.find_all('div', class_='product-price')

                # Extract and print the price from each div element
                for price_div in price_divs:
                    price_span = price_div.find('span',
                                                class_='value js-product-price-value custom-style-color-text-heading font-section-product-price')
                    if price_span:
                        price = price_span.get_text(strip=True)

        if price == "$0.00":
            price = "Free"
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    if next_page:
        print(f'Loading {next_page["href"]}')  # type: ignore
        response = httpx.get(next_page["href"], timeout=30.0, follow_redirects=True)  # type: ignore
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
