# finaccai/utils.py

import os
import time
import uuid
import logging
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from PIL import Image

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
SCREENSHOT_DIR = DATA_DIR / "screenshots"

for p in [DATA_DIR, SCREENSHOT_DIR]:
    p.mkdir(exist_ok=True, parents=True)


# -----------------------------
# Logging
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="[FinAccAI] %(levelname)s — %(message)s"
)

def log(msg):
    logging.info(msg)


# -----------------------------
# Page Acquisition
# -----------------------------

def load_static_html(url):
    """
    Download HTML via HTTP request (used for non-JS pages).
    """
    log(f"Fetching static page: {url}")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


def init_headless_browser():
    """
    Initialize Selenium Chrome headless browser.
    Used for JS-heavy financial dashboards.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")

    browser = webdriver.Chrome(options=chrome_options)
    return browser


def load_dynamic_page(url, wait=3):
    """
    Load page with Selenium, wait for scripts to render.
    Returns DOM + screenshot path.
    """
    log(f"Loading dynamic financial page: {url}")

    browser = init_headless_browser()
    browser.get(url)

    time.sleep(wait)

    html = browser.page_source

    screenshot_path = SCREENSHOT_DIR / f"{uuid.uuid4()}.png"
    browser.save_screenshot(str(screenshot_path))

    browser.quit()

    return html, screenshot_path


# -----------------------------
# DOM Parsing
# -----------------------------

def parse_dom(html):
    """
    Convert raw HTML into BeautifulSoup DOM.
    """
    return BeautifulSoup(html, "html.parser")


# -----------------------------
# Screenshot Utilities
# -----------------------------

def open_screenshot(path):
    return Image.open(path).convert("RGB")


# -----------------------------
# URL Utilities
# -----------------------------

def get_domain(url):
    return urlparse(url).netloc


# -----------------------------
# Unified Page Loader
# -----------------------------

def load_page(url, dynamic=False, wait=3):
    """
    Master loader used by FinAccAI pipeline.

    dynamic=False  → static HTTP request
    dynamic=True   → Selenium headless browser
    """
    if dynamic:
        html, screenshot = load_dynamic_page(url, wait=wait)
    else:
        html = load_static_html(url)
        screenshot = None

    dom = parse_dom(html)

    return dom, screenshot
