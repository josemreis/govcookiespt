from random import random
from typing import Optional, Union
import os
import sys
import time
import random
import json
import configparser
from pathlib import Path
from selenium.webdriver import Firefox
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PARENT_DIR = Path().resolve()
# parse config file and make it available to the entire module
config = configparser.ConfigParser()
config.read(os.path.join(PARENT_DIR, "config.ini"))
# generate somre relevant constants
PATH_TO_OPENWPM = config.get("openwpm", "path")
print(PATH_TO_OPENWPM)
sys.path.insert(0, PATH_TO_OPENWPM)
from openwpm.utilities.platform_utils import get_firefox_binary_path
from openwpm.deploy_browsers.selenium_firefox import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType

# paths for the output data
OUTPUT_DIR = "resources/governmental_websites/interm"
if not os.path.isdir(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "eportugal.json")
# should the client run in headless mode
HEADLESS = True
# standard sleep times
SLEEP_SHORT = 3
SLEEP_MEDIUM = 8
SLEEP_LONG = 30

PUBLIC_WEBSITE_DIRECTORIES = {
    "entidades": "https://eportugal.gov.pt/entidades/",
    "directorio_dos_sitios_publicos": "https://eportugal.gov.pt/diretorio-dos-sitios-publicos/-/pesquisa/search_cyberspace?_searchresults_formDate=1657019500131&_searchresults_keywords=&_searchresults_portalCategoryTypesId=&_searchresults_TipodeCanais+238346=on&_searchresults_checkboxNames=Categorias+238338%2CCategorias+238341%2CCategorias+238339%2CCategorias+238459%2CCategorias+238483%2CCategorias+1996102%2CCategorias+238336%2CCategorias+238340%2CCategorias+238492%2CAreasGovernativas+238357%2CAreasGovernativas+238521%2CAreasGovernativas+238361%2CAreasGovernativas+238360%2CAreasGovernativas+238519%2CAreasGovernativas+238358%2CAreasGovernativas+238512%2CAreasGovernativas+238359%2CAreasGovernativas+11216967%2CAreasGovernativas+238515%2CAreasGovernativas+238511%2CAreasGovernativas+238513%2CAreasGovernativas+238362%2CAreasGovernativas+238514%2CAreasGovernativas+238509%2CAreasGovernativas+238520%2CAreasGovernativas+238518%2CAreasGovernativas+238510%2CAreasGovernativas+238522%2CAreasGovernativas+238517%2CAreasGovernativas+238516%2CTipodeSites+238354%2CTipodeSites+238355%2CTipodeCanais+238347%2CTipodeCanais+238348%2CTipodeCanais+238346&pageSequenceNumber=2",
}


def deploy_firefox(
    firefox_binary_path: Optional[str] = None,
    headless: bool = False,
    geckodriver_log_path: Optional[str] = None,
    **kwargs,
) -> Firefox:
    """
    launches a firefox instance using the same browser version asgit OpenWPM
    """
    if not geckodriver_log_path:
        geckodriver_log_path = os.devnull
    firefox_binary_path = firefox_binary_path or get_firefox_binary_path()
    fo = Options()
    # run headlesss ?
    if headless:
        fo.add_argument("-headless")
    driver = Firefox(
        firefox_binary=firefox_binary_path,
        options=fo,
        service_log_path=geckodriver_log_path,
        **kwargs,
    )
    return driver


def visit_public_website_directory(driver: Firefox, url: str) -> None:
    """Visit the target website and accept cookies if needed"""
    driver.get(url)
    # accept cookies if needed
    _ = click(driver, "onetrust-button-group-parent")


def _find_element(
    driver: Firefox,
    element_id: Optional[str] = None,
    element_xpath: Optional[str] = None,
) -> Optional[WebElement]:
    """
    wait for an element to appear, if there click on it, else timeout.
    return a boolean for whether the button was clicked
    """
    if element_id:
        method = By.ID
        value = element_id
    elif element_xpath:
        method = By.XPATH
        value = element_xpath
    else:
        raise TypeError("You need to define an element_id or element_xpath")
    try:
        elem = driver.find_element(method, value)
        return elem
    except:
        pass


def click(
    driver_or_webelement: Union[Firefox, WebElement],
    element_id: Optional[str] = None,
    element_xpath: Optional[str] = None,
    timeout: int = 10,
) -> Optional[WebElement]:
    """
    wait for an element to appear, if there click on it, else timeout.
    return a boolean for whether the button was clicked
    """
    if element_id:
        method = By.ID
        value = element_id
    elif element_xpath:
        method = By.XPATH
        value = element_xpath
    else:
        raise TypeError("You need to define an element_id or element_xpath")
    button_present = True
    try:
        element = WebDriverWait(driver_or_webelement, timeout).until(
            EC.presence_of_element_located((method, value))
        )
    except:
        button_present = False
    if button_present:
        element.click()
        time.sleep(SLEEP_SHORT)
        return element


def accept_cookies(driver: Firefox) -> None:
    """If the cookie banner appears, accept all cookies"""
    click(driver, element_id="onetrust-button-group-parent")


def render_all_websites(driver: Firefox, **kwargs) -> None:
    """render all pages given the infinite loop for rendering pages present in the websites"""
    clicked = True
    while clicked:
        try:
            clicked = click(driver, "btnRenderMoreTen")
            time.sleep(random.uniform(SLEEP_SHORT, (SLEEP_SHORT * 2)))
        except:
            clicked = False


def select_websites_filter(driver: Firefox) -> None:
    """select the 'Websites' filter"""
    _ = click(
        driver,
        element_xpath="//div[@class = 'form-group form-inline input-checkbox-wrapper']",
    )


def parse_website_holder_element_directorio(element: WebElement) -> dict:
    """extract the relevant data from the webelement holding the website data"""
    anchor_tag = _find_element(element, element_xpath="./a")
    return {
        "url": anchor_tag.get_attribute("href"),
        "page_title": anchor_tag.text,
        "entity": _find_element(
            element, element_xpath="../div[@class = 'search-item-info']"
        ).text,
    }


def parse_website_holder_element_entidades(element: WebElement) -> dict:
    """extract the relevant data from the webelement holding the website data"""
    first_anchor_tag = _find_element(element, element_xpath="./h3/a")
    if first_anchor_tag:
        first_anchor_tag = first_anchor_tag.text
    url = _find_element(
        element, element_xpath="./div[@class = 'search-item-links pb-3']/a"
    )
    if url:
        url = url.get_attribute("href")
        if "https://eportugal.gov.pt/entidades/" in url:
            url = url.split("https://eportugal.gov.pt/entidades/")[1]
    return {
        "url": url,
        "page_title": first_anchor_tag,
        "entity": first_anchor_tag,
    }


def parse_website_holder_element(
    element: WebElement, is_directorio_dos_servicos_publicos: bool = True
) -> dict:
    """extract the relevant data from the webelement holding the website data"""
    if is_directorio_dos_servicos_publicos:
        return parse_website_holder_element_directorio(element)
    else:
        return parse_website_holder_element_entidades(element)


def collect_website_data(
    driver: Firefox,
    is_directorio_dos_serviços_publicos: bool = True,
) -> None:
    if is_directorio_dos_serviços_publicos:
        xpath = "//h3[@class = 'search-item-title']"
    else:
        xpath = "//div[@class = 'pl-3 pb-5 search-item']"
    website_header_elems = driver.find_elements(By.XPATH, xpath)
    if not website_header_elems:
        raise ValueError(f"Could not identify the elements with '{xpath}'.")
    website_data = {}
    for i, website_header in enumerate(website_header_elems):
        if website_header:
            website_data[i] = parse_website_holder_element(
                element=website_header,
                is_directorio_dos_servicos_publicos=is_directorio_dos_serviços_publicos,
            )
    return website_data


def main() -> None:
    """run the scraper"""
    driver = deploy_firefox(headless=HEADLESS)
    container = []
    for data_source, url in PUBLIC_WEBSITE_DIRECTORIES.items():
        is_sitios_publicos = False
        if "sitios" in data_source:
            is_sitios_publicos = True
        visit_public_website_directory(driver=driver, url=url)
        if is_sitios_publicos:
            select_websites_filter(driver)
        render_all_websites(driver)
        container.append(
            collect_website_data(
                driver=driver, is_directorio_dos_serviços_publicos=is_sitios_publicos
            )
        )
    # merge them
    i = 0
    website_data = {}
    urls_added = set()
    for source_dict in container:
        for _, cur_dict in source_dict.items():
            if cur_dict.get("url") not in urls_added:
                website_data[i] = cur_dict
                i += 1
    with open(OUTPUT_PATH, "w") as f:
        json.dump(website_data, f, indent=4, ensure_ascii=False)
    driver.close()
    driver.quit()


if __name__ == "__main__":
    main()
