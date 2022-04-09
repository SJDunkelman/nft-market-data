import common
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


def scrape_top_collections():
    fungible_url = 'https://nonfungible.com/market-tracker?segment=collectible&days=9007199254740991'
    driver = common.open_selenium_driver()
    driver.get(fungible_url)
    time.sleep(4)
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/section/div/div[7]/div[2]/table/tbody'))
    )
    # table = driver.find_element(By.CLASS_NAME, 'MuiTableContainer-root')
    coordinates = table.location_once_scrolled_into_view
    print(coordinates)
    driver.execute_script(f'window.scrollTo({coordinates["x"]}, {coordinates["y"]});')
    time.sleep(10)


def scrape_collection(name):
    url = f'https://nonfungible.com/market-tracker/{name}'
    driver = common.open_selenium_driver()
    driver.switch_to.window(driver.window_handles[1])
    driver.get(url)
    time.sleep(5)
    driver.execute_script(f'window.scrollTo(0, 2022);')



if __name__ == "__main__":
    # scrape_top_collections()
    scrape_collection('boredapeclub')
