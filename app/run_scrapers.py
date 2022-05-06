import os
import subprocess
from pathlib import Path

from my_funcs import update_vendor_counts


def main() -> None:

    scrapers_path = Path.cwd() / "scrapers"
    scrapers = sorted(scrapers_path.glob("*.py"))

    for scraper in scrapers:
        if scraper.stem == "__init__":
            continue
        if os.name != "posix" and scraper.name == "ai.py":
            continue
        print(f"Loading {scraper}")
        result = subprocess.run(["python", scraper])
        
    update_vendor_counts.main()
    print("Scraping complete.")


if __name__ == "__main__":
    main()
