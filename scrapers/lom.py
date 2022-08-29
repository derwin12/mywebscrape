import os
from urllib.parse import urljoin

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

storename = "Lights on Mamie"
lastval = ""
pageno = 1


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    global lastval, pageno
    exitloop = False
    products = soup.find_all(class_="grid-product__wrap")
    if len(products) == 0:
        exitloop = True

    sequences = []
    for i, product in enumerate(products):
        sequence_name = product.find(class_="grid-product__title").text.strip()
        if i == 0:
            if lastval == sequence_name:
                exitloop = True
                break
            else:
                lastval = sequence_name

        if any(x in sequence_name for x in ["MAGICOLOUR", "Custom"]):
            continue
        product_url = urljoin(url, product.find(class_="grid-product__title")["href"])
        price = product.find(class_="grid-product__price-amount").text.strip()
        if price == "$0":
            price = "Free"
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )
    if not exitloop:
        next_page = soup.find_all(class_="pager__button-text")

        for np in next_page:
            if np.text == 'Next':
                print(f'Loading {url + "/?offset=" + str(9*pageno) }')  # type: ignore
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
                driver.get(url + "/?offset=" + str(9*pageno))  # type: ignore
                pageno = pageno + 1
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
