import os
import re
from dataclasses import dataclass
from urllib.parse import urljoin

from app import BaseUrl, Sequence, Vendor
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

storename = "Custom Light Creations"
lastval = ""
pagecnt = 0


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    global lastval, pagecnt
    exitloop = False
    pagecnt += 1
    products = soup.find_all(
        "a",
        attrs={
            "role": "link",
            "data-aid": re.compile("^PRODUCT_NAME_RENDERED"),
            },
    )
    sequences = []
    if products and pagecnt < 15:  # Put in a safety to avoid endless looping
        for i, product in enumerate(products):
            sequence_name = product.find("h4").text.strip()
            if i == 0:
                if lastval == sequence_name:
                    exitloop = True
                    break
                else:
                    lastval = sequence_name

            # song, artist = sequence_name.split(" - ")
            product_url = urljoin(url, product.attrs["href"])
            pattern = re.compile(r"(\$\d[\d,.]*)")
            price_text = pattern.search(product.text)
            if price_text:
                price = price_text[1]
            else:
                print(f"Problems with {sequence_name}")
                price = "-"
            if price == "$0.00":
                price = "Free"
            sequences.append(
                Sequence(
                    name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
                )
            )
        if not exitloop:
            next_page = soup.find(attrs={"data-aid": "PAGINATION_ARROW_FORWARD"})

            if next_page:
                print(f'Loading {urljoin(url, next_page["href"])}')  # type: ignore
                if os.name != "posix":
                    service_object = Service.Service(binary_path)
                    driver = webdriver.Chrome(service=service_object)
                else:
                    options = Options()
                    options.add_argument("--headless")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    driver = webdriver.Chrome(
                        service=Service("/usr/bin/chromedriver"), options=options
                    )
                driver.get(urljoin(url, next_page["href"]))  # type: ignore
                try:
                    WebDriverWait(driver, 20).until(
                        expected_conditions.element_to_be_clickable((By.LINK_TEXT, "1"))
                    )
                except TimeoutException:
                    print("Unable to load")
                html = driver.page_source
                driver.close()
                next_soup = BeautifulSoup(html, "html.parser")
                sequences.extend(
                    get_products_from_page(soup=next_soup, url=url, vendor=vendor)
                )

    return sequences


def document_initialised(driver):
    return driver.execute_script("return")


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    for url in vendor.urls:
        print(f"Loading {url.url}")
        if os.name != "posix":
            service_object = Service.Service(binary_path)
            driver = webdriver.Chrome(service=service_object)
        else:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(
                service=Service("/usr/bin/chromedriver"), options=options
            )

        driver.get(url.url)
        try:
            WebDriverWait(driver, 20).until(
                expected_conditions.element_to_be_clickable((By.LINK_TEXT, "1"))
            )
        except TimeoutException:
            print("Unable to load")
            pass
        html = driver.page_source
        driver.close()
        soup = BeautifulSoup(html, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
