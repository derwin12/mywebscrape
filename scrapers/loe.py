from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app import Sequence, Vendor
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "LOE Sequences"


def get_products_from_page(soup: BeautifulSoup, url: str, vendor: Vendor) -> list[Sequence]:
    # This is the working selector in Jan 2026 on this exact store
    products = soup.select('li.grid__item.grid__item--collection-template')

    sequences = []
    for product in products:
        title_tag = product.select_one('.grid-view-item__title')
        if not title_tag:
            continue
        sequence_name = title_tag.get_text(strip=True)

        if any(x in sequence_name.lower() for x in ["pre-buy", "custom", "coming soon", "sold out"]):
            print("Skip", sequence_name)
            continue

        link_tag = product.select_one('a.grid-view-item__link')
        if not link_tag or 'href' not in link_tag.attrs:
            continue
        product_url = urljoin(url, link_tag['href'])

        # Price – take the lowest visible price (sale or regular)
        price_tags = product.select('.price-item--regular, .price-item--sale')
        prices = []

        for tag in price_tags:
            text = tag.get_text(strip=True)
            if not text or 'from' not in text.lower():
                continue
            # Clean: remove "from ", "$", commas
            cleaned = text.lower().replace('from', '').replace('$', '').replace(',', '').strip()
            try:
                prices.append(float(cleaned))
            except ValueError:
                continue

        if prices:
            price_float = min(prices)
            price_str = f"${price_float:.2f}" if price_float > 0 else "Free"
        else:
            price_str = "Contact store"
            print(f"No valid price found for: {sequence_name}")

        sequences.append(
            Sequence(
                name=sequence_name,
                vendor_id=vendor.id,
                link=product_url,
                price=price_str
            )
        )

    # Pagination (your current code is fine, but improved robustness)
    next_page = soup.select_one('a.next')
    if next_page and 'href' in next_page.attrs:
        next_url = urljoin(url, next_page['href'])
        time.sleep(2.5)  # polite delay
        response = httpx.get(next_url, timeout=30.0, follow_redirects=True,
                            headers={"User-Agent": "Mozilla/5.0 SequenceScraper/1.0"})
        if response.status_code == 200:
            next_soup = BeautifulSoup(response.text, "html.parser")
            sequences.extend(get_products_from_page(next_soup, url, vendor))  # keep base url

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
