import cloudscraper
import common
from bs4 import BeautifulSoup
import math
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2_1) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/98.0.4758.102 Safari/537.36"}


"""
My first attempt at OS
"""
# rankings_url = 'https://opensea.io/rankings?sortBy=total_volume'
#
#
# def scrape_top_collections(top_n: int = 500):
#     driver = common.open_selenium_driver()
#     driver.get(rankings_url)
#
#     # # Check for cloudflare
#     # try:
#     #     button = driver.find_element_by_xpath('//*[@id="__next"]/div[1]/div[2]/div/div[1]/div[2]/div[1]/div/div/button')
#     # except:
#     #     i = input('Have you countered cloudflare with new IP? (y/n)')
#     #     if i.lower() == 'y':
#     #         driver.get(coin_market_url)
#
#     page_height = driver.execute_script("return document.body.scrollHeight")
#     window_height = driver.execute_script('return window.innerHeight')
#
#     driver.execute_script("window.scrollTo(0, 0);")
#     collections = []
#     for i in range(math.ceil(page_height/window_height)):
#         html = driver.page_source.encode("utf-8")
#         soup = BeautifulSoup(html, 'lxml')
#         collections.append(find_all_collections(soup))
#         driver.execute_script(f"window.scrollBy(0, {i * window_height})")
#         time.sleep(4)
#     return collections
#
#     # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#
#
# def find_all_collections(soup):
#     collections = []
#     rows = soup.find_all(attrs={'role': 'listitem'})
#     for row in rows:
#         try:
#             title = row.find('div', {'class': 'Ranking--collection-name-overflow'}).text
#             owners = row.find_all('p', {'class': 'kWYeTM'})[0].text
#             items = row.find_all('p', {'class': 'kWYeTM'})[1].text
#             volume = row.find_all('div', {'class': 'jPSCbX'})[2].text
#             floor_price = row.find_all('div', {'class': 'jPSCbX'})[-1].text
#             collections.append({
#                 'title': title,
#                 'owners': owners,
#                 'items': items,
#                 'volume': volume,
#                 'floor_price': floor_price
#             })
#         except:
#             print("row failed")
#     return collections



"""
My second attempt at CMC
"""

def get_first_string(element):
    """
    Get the first string in a div without the percentage underneath
    :param element:
    :return:
    """
    text = str(element).split('<br/>')[0]
    return re.sub(r'(<.+>)', '', text)


"""
My third attempt at CMC
"""

def scrape_coinmarketcap_nfts():
    coinmarketcap_url = 'https://coinmarketcap.com/nft/collections'
    html = scraper.get(coinmarketcap_url)
    soup = BeautifulSoup(html.text, 'lxml')
    page_numbers = [int(p.text) for p in soup.find_all('li', {'class': 'page'})]
    total_pages = page_numbers[-1]

    driver = common.open_selenium_driver()

    data = []
    failed = {}
    for page_idx in range(1, total_pages+1):
        print(f'Scraping page {page_idx}')
        start_time = time.time()
        coinmarketcap_url = f'https://coinmarketcap.com/nft/collections/?page={page_idx}'
        driver.switch_to.default_content()
        driver.get(coinmarketcap_url)
        page_height = driver.execute_script("return document.body.scrollHeight")
        window_height = driver.execute_script('return window.innerHeight')
        driver.execute_script("window.scrollTo(0, 0);")
        all_time_button = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/div[2]/div/div/div[1]/div/button[4]')
        all_time_button.click()

        page_failed = []
        for i in range(math.ceil(page_height / window_height) - 2):
            html = driver.page_source.encode("utf-8")
            soup = BeautifulSoup(html, 'lxml')
            table = soup.find('table', {'class': 'cmc-table'})
            rows = table.find_all('tr')
            driver.execute_script(f"window.scrollBy(0, {i * window_height})")
            time.sleep(4)
            for row in rows[1:]:
                cells = row.find_all('td')
                collection = {}
                row_id = cells[0].text
                try:
                    collection['id'] = row_id
                except:
                    print('No row ID')
                try:
                    collection['name'] = cells[1].find_all('span')[0].text
                except:
                    print(f'failed on name for {row_id}')
                    page_failed.append(row_id)
                try:
                    collection['chain'] = cells[1].find_all('span')[1].text
                except:
                    print(f'failed on chain for {row_id}')
                    page_failed.append(row_id)
                try:
                    collection['volume'] = get_first_string(cells[2])
                except:
                    print(f'failed on volume for {row_id}')
                    page_failed.append(row_id)
                try:
                    collection['market_cap'] = cells[3].text
                except:
                    print(f'failed on market_cap for {row_id}')
                    page_failed.append(row_id)
                try:
                    collection['floor_price'] = cells[4].text
                except:
                    print(f'failed on floor for {row_id}')
                    page_failed.append(row_id)
                try:
                    collection['avg_price'] = get_first_string(cells[5])
                except:
                    print(f'failed on avg price for {row_id}')
                    page_failed.append(row_id)
                try:
                    collection['sales'] = get_first_string(cells[6])
                except:
                    print(f'failed on sales for {row_id}')
                    page_failed.append(row_id)
                try:
                    collection['assets'] = cells[7].text
                except:
                    print(f'failed on assets for {row_id}')
                    page_failed.append(row_id)
                try:
                    collection['owners'] = cells[8].text
                except:
                    print(f'failed on owners for {row_id}')
                    page_failed.append(row_id)

                data.append(collection)

            failed[i] = page_failed

            # Check if end of page
            # nav_bar = driver.find_element(By.CLASS_NAME, 'bvcQcm')
            # if nav_bar.is_displayed():
            #     break


        print(f'scraped in {round(time.time() - start_time, 2)} seconds')
    return data, failed


if __name__ == "__main__":
    data, failed = scrape_coinmarketcap_nfts()
