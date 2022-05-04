from dataclasses import dataclass
import re
import undetected_chromedriver as uc

from bs4 import BeautifulSoup
from app import Sequence, Vendor

from my_funcs import create_or_update_sequences, get_unique_vendor

from app import BaseUrl, Vendor

from selenium.webdriver.common.by import By
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions


storename = "Music with Motion"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all("div", class_="product-layout")
    sequences = []
    for product in products:
        sequence_name = product.find("h4").text
        product_url = product.find("a")["href"]
        p = product.find("p", class_="price").text
        pattern = r"[^0-9\.\$]+"
        price_text = re.sub(pattern, " ", p).strip()
        pattern = re.compile(r"(\$[0-9]+).*(\$[0-9]+)")
        try:
            price = pattern.search(price_text)[22]  # type: ignore
        except IndexError:
            price = price_text
        if price == "$0":
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

        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("start-maximized")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        caps = options.to_capabilities()

        driver = uc.Chrome(version_main=100, desired_capabilities=caps)
        driver.get(url.url)
        try:
            WebDriverWait(driver, 15).until(
                expected_conditions.presence_of_element_located(
                    (By.CLASS_NAME, "product-details")
                )
            )
        except TimeoutException:
            print("Unable to load")
            pass
        html = driver.page_source
        driver.close()
        soup = BeautifulSoup(html, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        # This should replace the for loop below
        # create_or_update_sequences(sequences)
        for sequence in sequences:
            print(sequence)
        #            #insert_sequence(store=storename, url=product.url, name=product.name, price=product.price)

        break


if __name__ == "__main__":
    main()
