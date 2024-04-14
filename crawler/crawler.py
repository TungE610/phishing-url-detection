from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

class Phisherman:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.success = 0
        self.driver = None

    def __enter__(self):
        self.driver = webdriver.Firefox()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()

    def make_page_url(self, page):
        return f"https://www.phishtank.com/phish_search.php?page={page}&active=y&valid=y&Search=Search"

    def make_detail_page_url(self, url_id):
        return f"https://www.phishtank.com/phish_detail.php?phish_id={url_id}"

    def get_ids(self, page):
        print(f"Gathering links from page [{page}]... ", end="")
        self.driver.get(self.make_page_url(page))
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".value:first-child > a")))
            elements = self.driver.find_elements(By.CSS_SELECTOR, ".value:first-child > a")
            url_ids = [element.text for element in elements]
            print("Success")
            return url_ids
        except Exception as e:
            print(f"Error: {e}")
            return []

    def get_data(self, url_id):
        print(f"Gathering data for url [id={url_id}]... ", end="")
        self.driver.get(self.make_detail_page_url(url_id))
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".padded > div:nth-child(4) > span:nth-child(1) > b:nth-child(1)")))
            phish_url = self.driver.find_element(By.CSS_SELECTOR, ".padded > div:nth-child(4) > span:nth-child(1) > b:nth-child(1)").text
            self.success += 1
            print("Success")
            # Write only the URL to CSV
            with open('phishing_url.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([phish_url])
        except Exception as e:
            print(f"Error: {e}")

    def crawl(self):
        print("Start crawling! Phisherman is gathering data... ")
        for page in range(self.start, self.end + 1):
            result = self.get_ids(page)
            if result:
                for url_id in result:
                    self.get_data(url_id)

        print(f"Crawling complete! Successfully gathered {self.success} URLs")

def main():
    start, end = 1, 2  # Default start and end page numbers
    try:
        start = int(input("Enter start page number: "))
        end = int(input("Enter end page number: "))
    except ValueError:
        print("Invalid input. Using default values.")

    with Phisherman(start, end) as phisherman:
        phisherman.crawl()

if __name__ == "__main__":
    main()
