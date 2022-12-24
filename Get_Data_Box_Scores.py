# Importing Libraries
import os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time

# Getting data from 2015-16 season to 2021-2022 season
SEASONS = list(range(2016,2023))

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


standings_files = os.listdir(STANDINGS_DIR)

# Scraping individual box scores from each Game
def scrape_game(standings_file):
    with open(standings_file, 'r') as f:
        html = f.read()

    soup = BeautifulSoup(html, features="html.parser")
    links = soup.find_all("a")
    hrefs = [l.get('href') for l in links]
    box_scores = [f"https://www.basketball-reference.com{l}" for l in hrefs if l and "boxscore" in l and '.html' in l]

    for url in box_scores:
        save_path = os.path.join(SCORES_DIR, url.split("/")[-1])
        if os.path.exists(save_path):
            continue

        html = get_html(url, "#content")
        if not html:
            continue
        with open(save_path, "w+") as f:
            f.write(html)


import pandas as pd
for season in SEASONS:
    files = [s for s in standings_files if str(season) in s]
    
    for f in files:
        filepath = os.path.join(STANDINGS_DIR, f)
        
        scrape_game(filepath)