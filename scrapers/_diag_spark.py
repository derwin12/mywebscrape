import sys

sys.path.insert(0, ".")
from scrapers.sparktolight import make_driver

driver = make_driver()
try:
    driver.get("https://sparktolights.com/collection/all")
    import time

    time.sleep(10)
    print("TITLE:", driver.title)
    print("URL:", driver.current_url)
    src = driver.page_source
    print("LENGTH:", len(src))
    print(src[:2000])
finally:
    driver.quit()
