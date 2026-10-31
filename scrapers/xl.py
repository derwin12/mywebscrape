import argparse
import re
from urllib.parse import urljoin

from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor, http_get, limit_pagination


storename = "xLightsSequences"


@limit_pagination
def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor, follow_next: bool = True
) -> list[Sequence]:

    products = soup.find_all("div", class_="structItem")
    sequences = []
    pattern = r"[^A-Za-z0-9\-\'\.()&]+"
    for product in products:
        category = product.find("a", class_="labelLink").text.lower()
        s = (
            product.find("div", class_="structItem-title")
            .find("a", attrs={"data-tp-primary": "on"})
            .text
        )
        sequence_name = re.sub(pattern, " ", s).strip()
        if sequence_name == "Thunderstruck - AC DC":
            print(f"Testing")
        if any(x in category.lower() for x in ["model", "vendor"]):
            print(f"Skipping ({category}) {sequence_name}")
            continue
        if any(x in sequence_name.lower() for x in ["delete"]):
            print(f"Skipping {sequence_name}")
            continue
        product_url = urljoin(
            url,
            product.find("div", class_="structItem-title").find(
                "a", attrs={"data-tp-primary": "on"}
            )["href"],
        )
        price_text = product.find("span", class_="label--primary")
        username = product.find('a', class_='username').text.strip()
        if username == "lightlink":
            print(f"Skipping {username} {sequence_name}")
            continue
        price = price_text.text if price_text else "Free"
        if price == "0.00":
            price = "Free"
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )
    next_page = soup.find(class_="pageNav-jump pageNav-jump--next")
    if next_page and follow_next:
        next_page_url = urljoin(url, soup.find("a", class_="pageNav-jump pageNav-jump--next")["href"])  # type: ignore
        print(f"Loading {next_page_url}")
        response = http_get(next_page_url, timeout=30.0)
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.extend(get_products_from_page(soup=next_soup, url=url, vendor=vendor))

    return sequences


def main(file: str | None = None, dry_run: bool = False) -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    if file:
        # The site blocks scrapers with a bot check, so parse a page saved from a browser instead.
        # Links are resolved against the vendor URL, and next-page links are not followed.
        print(f"Loading saved page {file}")
        with open(file, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        sequences = get_products_from_page(
            soup=soup, url=vendor.urls[0].url, vendor=vendor, follow_next=False
        )
        print(f"Found {len(sequences)} sequences in saved page")
        if not sequences:
            raise SystemExit("No sequences found; is this a saved xlightsseq.com/sequences/ page?")
        if dry_run:
            for seq in sequences:
                print(f"  {seq.name} | {seq.price} | {seq.link}")
            return
        create_or_update_sequences(sequences)
        return

    for url in vendor.urls:
        print(f"Loading {url.url}")
        response = http_get(url.url, timeout=30.0)
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Scrape {storename}")
    parser.add_argument("--file", help="parse a saved HTML page instead of fetching the site")
    parser.add_argument("--dry-run", action="store_true", help="with --file, list sequences without saving")
    args = parser.parse_args()
    main(file=args.file, dry_run=args.dry_run)
