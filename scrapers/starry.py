from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app import Sequence, Vendor
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "Starry Night Display"


def get_products_from_page(
        soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    # Correct product container selector for this site
    products = soup.select('li.entry.product.type-product')

    sequences = []
    for product in products:
        # Title – use the correct WooCommerce class
        title_tag = product.select_one('h2.woocommerce-loop-product__title')
        if not title_tag:
            continue
        sequence_name = title_tag.get_text(strip=True)

        if any(x in sequence_name.lower() for x in ["pre-buy", "custom", "coming soon"]):
            print("Skip:", sequence_name)
            continue

        # Product link – take from the main product link
        link_tag = product.select_one('a.woocommerce-LoopProduct-link')
        if not link_tag or 'href' not in link_tag.attrs:
            continue
        product_url = urljoin(url, link_tag['href'])

        # Price – take the visible price (handles both regular and sale)
        price_tag = product.select_one('span.woocommerce-Price-amount.amount')
        if not price_tag:
            print("No price found for:", sequence_name)
            continue

        text = price_tag.get_text(strip=True)
        # Clean: remove currency symbol, "from", commas, etc.
        cleaned = text.replace('$', '').replace('from', '').replace(',', '').strip()
        try:
            price_float = float(cleaned)
            price_str = f"${price_float:.2f}" if price_float > 0 else "Free"
        except ValueError:
            price_str = "Contact store"
            print(f"Bad price format '{text}' for: {sequence_name}")

        sequences.append(
            Sequence(
                name=sequence_name,
                vendor_id=vendor.id,
                link=product_url,
                price=price_str
            )
        )

    # Pagination – this part was already mostly correct, but make it safer
    next_link = soup.select_one('a.next.page-numbers')
    if next_link and 'href' in next_link.attrs:
        next_url = urljoin(url, next_link['href'])
        print(f"→ Next page: {next_url}")

        # Add polite delay + headers (prevents 403 on next pages too)
        time.sleep(random.uniform(2.0, 4.0))
        response = httpx.get(
            next_url,
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

        if response.status_code == 200:
            next_soup = BeautifulSoup(response.text, "html.parser")
            sequences.extend(get_products_from_page(next_soup, url, vendor))
        else:
            print(f"Pagination failed: {response.status_code} on {next_url}")

    return sequences


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    for url in vendor.urls:
        print(f"Loading {url.url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

        response = httpx.get(
            url.url,
            timeout=30.0,
            follow_redirects=True,
            headers=headers
        )
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
