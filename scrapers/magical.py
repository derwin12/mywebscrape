import re
import os
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app import Sequence, Vendor
from my_funcs import create_or_update_sequences, get_unique_vendor

if os.name != "posix":
    import selenium.webdriver.chrome.service as Service
    from chromedriver_py import binary_path
else:
    from selenium.webdriver.chrome.service import Service

storename = "Magical Light Shows"
max_scrolls = 10


def get_products_from_page(soup: BeautifulSoup, url: str, vendor: Vendor) -> list[Sequence]:
    products = soup.find_all("div", class_="card product-card product-card--card flex flex-col leading-none relative")
    print(f"Found {len(products)} products")
    sequences = []

    for product in products:
        content_div = product.find("div", class_="product-card__content")
        if not content_div:
            continue

        title_tag = content_div.find("a", class_="product-card__title")
        if not title_tag:
            continue
        sequence_name = re.sub(r"[^A-Za-z0-9\-\'\.()&]+", " ", title_tag.text.strip())
        product_url = urljoin(url, title_tag["href"])

        if "plan members" in sequence_name.lower() or "laser" in sequence_name.lower() or "membership" in sequence_name.lower():
            continue

        price_div = product.find("div", class_=re.compile(r"price(\sprice--on-sale)?"))
        if not price_div:
            continue

        sale_price_tag = price_div.find("span", class_="price__regular")
        regular_price_tag = price_div.find("span", class_="price__sale")

        price = sale_price_tag.text.strip() if sale_price_tag else regular_price_tag.text.strip() if regular_price_tag else None
        if not price:
            continue

        match = re.search(r"\$([\d.]+)", price)
        if match:
            price = f"${match.group(1)}"
        else:
            continue

        if price == "$0.00":
            price = "Free"

        sequences.append(Sequence(name=sequence_name, vendor_id=vendor.id, link=product_url, price=price))
        print(f"Added sequence: {sequence_name}, Price: {price}, URL: {product_url}")

    return sequences


def load_dynamic_page(url: str) -> BeautifulSoup:
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = None
    try:
        options = Options()
        options.add_argument("--headless=new")  # Use modern headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        if os.name != "posix":
            service = Service.Service(binary_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(
                service=Service("/usr/bin/chromedriver"), options=options
            )

        driver.get(url)
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-card__title"))
            )
            print("Initial page loaded")
        except TimeoutException:
            print("Timeout waiting for initial products")

        scroll_count = 0
        last_height = driver.execute_script("return document.body.scrollHeight")
        last_product_count = 0
        no_change_scrolls = 0  # Count of consecutive scrolls with no new products

        while scroll_count < max_scrolls and no_change_scrolls < 3:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Wait up to 10s for new products to appear
            current_product_count = 0
            for _ in range(10):
                current_products = driver.find_elements(By.CLASS_NAME, "product-card")
                current_product_count = len(current_products)
                if current_product_count > last_product_count:
                    break
                time.sleep(1)

            if current_product_count == last_product_count:
                no_change_scrolls += 1
            else:
                no_change_scrolls = 0  # Reset if we found new products

            print(f"Scroll {scroll_count + 1}: {current_product_count} products")
            last_product_count = current_product_count
            scroll_count += 1

        time.sleep(5)  # Final wait
        final_products = len(driver.find_elements(By.CLASS_NAME, "product-card"))
        print(f"Final check: {final_products} sequences loaded")

        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved page source to debug.html")

        soup = BeautifulSoup(driver.page_source, "html.parser")

    except Exception as e:
        print(f"Error loading page: {e}")
        raise
    finally:
        if driver is not None:
            driver.quit()

    return soup


def main() -> None:
    print(f"Loading {storename} at {time.strftime('%H:%M:%S')}")
    vendor = get_unique_vendor(storename)

    for url in vendor.urls:
        print(f"Loading {url.url}")
        try:
            soup = load_dynamic_page(url.url)
            sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)
            print(f"Total sequences found: {len(sequences)}")
            create_or_update_sequences(sequences)
        except Exception as e:
            print(f"Failed to process {url.url}: {e}")
            continue


if __name__ == "__main__":
    main()
