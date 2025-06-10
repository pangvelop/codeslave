import time
from urllib.parse import urljoin

from bs4 import NavigableString, BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_rendered_html(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(3)  # 동적 콘텐츠 로딩 대기
    html = driver.page_source
    driver.quit()
    return html


def extract_element(element, base_url=None):
    if isinstance(element, NavigableString):
        return element.strip()
    if element.name in ['script', 'style']:
        return ""
    if element.name in ['a', 'img']:
        if element.name == 'img' and base_url:
            src = element.get('src')
            if src and not src.startswith('http'):
                element['src'] = urljoin(base_url, src)
        return str(element)
    result = ""
    for child in element.children:
        child_text = extract_element(child, base_url)
        if child_text:
            result += child_text + " "
    return result.strip()


def extract_content(html, target_class=None, base_url=None):
    soup = BeautifulSoup(html, 'html.parser')
    if target_class:
        container = soup.find(class_=target_class)
        element = container if container else soup
    else:
        element = soup
    return extract_element(element, base_url)
