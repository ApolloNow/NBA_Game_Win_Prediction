# Importing Libraries
import os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time

# Getting data from 2015-16 season to 2021-2022 season
SEASONS = list(range(2019,2023))

# Data Save path folder and file
DATA_DIR = "data"
STANDINGS_DIR = os.path.join(DATA_DIR, "standings")
SCORES_DIR = os.path.join(DATA_DIR, "scores")



def get_html(url, selector, sleep=0, retries=3):
    html = None
    for i in range(1, retries+1):
        time.sleep(sleep * i)
        try:
            with sync_playwright() as p:
                # Opening chromium based browser for scraping
                browser = p.chromium.launch()
                # Opening new tab/page
                page = browser.new_page()
                # Browsing to our desired urd
                page.goto(url)
                print(page.title())
                # Selecting only desired html content from that page
                html = page.inner_html(selector)
        except PlaywrightTimeout:
            print(f"Timeout error on {url}")
            continue
        else:
            break
    return html

def scrape_season(season):
    url = f"https://www.basketball-reference.com/leagues/NBA_{season}_games.html"
    # Getting html content with id=content and class=filter
    html = get_html(url, "#content .filter")
    
    soup = BeautifulSoup(html)
    links = soup.find_all("a")
    standings_pages = [f"https://www.basketball-reference.com{l['href']}" for l in links]
    
    # Writing table with all scheduled games within a month to a particular file
    for url in standings_pages:
        save_path = os.path.join(STANDINGS_DIR, url.split("/")[-1])
        if os.path.exists(save_path):
            continue
        
        html = get_html(url, "#all_schedule")
        with open(save_path, "w+") as f:
            f.write(html)


# Scraping for all seasons from 2016 to 2022
for season in SEASONS:
    scrape_season(season)