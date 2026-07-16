import os
import re

from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

if os.name != "posix":
    import selenium.webdriver.chrome.service as Service
    from chromedriver_py import binary_path
else:
    from selenium.webdriver.chrome.service import Service

storename = "Spark To Light"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def make_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"--user-agent={USER_AGENT}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if os.name != "posix":
        service_object = Service.Service(binary_path)
        return webdriver.Chrome(service=service_object, options=options)
    else:
        return webdriver.Chrome(
            service=Service("/usr/bin/chromedriver"), options=options
        )


def load_soup(driver, url: str) -> BeautifulSoup:
    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "product-card-wrapper")
            )
        )
    except TimeoutException:
        print(f"Timeout waiting for products on {url}")
    return BeautifulSoup(driver.page_source, "html.parser")


def get_price(driver, product_url: str) -> str:
    price = "Unknown"
    soup = load_soup(driver, product_url)
    price_divs = soup.find_all("div", class_="product-price")
    for price_div in price_divs:
        price_span = price_div.find(
            "span",
            class_="value js-product-price-value custom-style-color-text-heading font-section-product-price",
        )
        if price_span:
            price = price_span.get_text(strip=True)
    return price


def get_products_from_page(
    driver, soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all(
        "div", class_="card-wrapper product-card-wrapper underline-links-hover"
    )

    page_links = soup.find_all("a", href=re.compile(r"page=", re.I))
    next_page = None
    for link in page_links:
        text = link.get_text(strip=True)
        if "next" in text.lower():
            next_page = link
            break

    sequences = []
    for product in products:
        heading = product.find(
            "h3",
            class_="card__heading font-section-collection-productName builder-pointer-events-all-in-color-tweaks-manager",
        )
        sequence_name = heading.get_text(strip=True)
        product_url = heading.find("a")["href"]

        price = get_price(driver, product_url) if product_url else "Unknown"
        if price == "$0.00":
            price = "Free"

        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    if next_page:
        print(f'Loading {next_page["href"]}')  # type: ignore
        next_soup = load_soup(driver, next_page["href"])  # type: ignore
        sequences.extend(
            get_products_from_page(driver, soup=next_soup, url=url, vendor=vendor)
        )

    return sequences


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    for url in vendor.urls:
        print(f"Loading {url.url}")
        driver = make_driver()
        try:
            soup = load_soup(driver, url.url)
            sequences = get_products_from_page(
                driver, soup=soup, url=url.url, vendor=vendor
            )
            create_or_update_sequences(sequences)
        finally:
            driver.quit()


if __name__ == "__main__":
    main()
