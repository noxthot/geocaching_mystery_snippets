import json
import os
import re
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from selenium import webdriver


_BASE_URL = "https://www.geocaching.com"

URLS = {
    "cache_details": urljoin(_BASE_URL, "seek/cache_details.aspx"),
    "geocache": urljoin(_BASE_URL, "geocache"),
    "login": urljoin(_BASE_URL, "account/signin"),
    "list": urljoin(_BASE_URL, "plan/lists"),
}

_USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0"


def _to_decimal(coord_str):
    _, coord_deg, coord_min = coord_str.replace("°", "").replace("'", "").split(" ")

    return round(int(coord_deg) + float(coord_min) / 60, 5)


def get_session():
    session = requests.Session()

    # Login geocaching.com
    login_page_req = session.request(method="GET", url=URLS["login"])
    login_page = BeautifulSoup(login_page_req.text, "html.parser")
    token_field_name = "__RequestVerificationToken"
    token_value = login_page.find("input", attrs={"name": token_field_name})["value"]

    config_path = os.path.join("config.json")

    if os.path.exists(config_path):
        print("Loading credentials from config.")
        with open(config_path, "r") as file:
            config = json.load(file)
            myuser = config.get("username", None)
            mypsw = config.get("password", None)
            allow_clipboard = config.get("allow_clipboard", None)
    else:
        print("No config provided. Ask user for credentials.")
        myuser = input("Your geocaching.com username: ")
        mypsw = input("Your geocaching.com password: ")
        allow_clipboard_input = input("Do you want to have the calculated coordinates copied into your clipboard automatically (y/n)?: ")
        allow_clipboard = (allow_clipboard_input.lower() in ["y", "j", "yes"])

    post = {
        "UsernameOrEmail": myuser,
        "Password": mypsw,
        token_field_name: token_value
    }

    after_login_page = session.request(method="POST", url=URLS["login"], data=post)

    if "Sign out" in after_login_page.text:
        print("Login successful")
    else:
        raise Exception("Login failed")

    return {"session": session, "allow_clipboard": allow_clipboard}


def set_user_coordinate(session, gc_code, lat_str, lon_str):
    lat_dec = _to_decimal(lat_str)
    lon_dec = _to_decimal(lon_str)

    uri_usertoken = f"{URLS["cache_details"]}?wp={gc_code.upper()}"

    page_usertoken = session.get(uri_usertoken, headers={"Referer" : uri_usertoken})

    res = re.search('userToken = \'(.*)\';', page_usertoken.text)

    if not(res):
        raise Exception("Could not find userToken")

    userToken = res.group(1)

    post_data = {
        "dto": {
            "data": {
                "lat": lat_dec,
                "lng": lon_dec,
            },
            "ut": userToken,
        },
    }

    uri_suc = f"{URLS["cache_details"]}/SetUserCoordinate"

    after_request = session.post(
                                    uri_suc,
                                    allow_redirects=False,
                                    headers={"User-Agent" : _USER_AGENT, "Referer" : uri_suc},
                                    json=post_data
    )

    if after_request.status_code == 200:
        print(f"Coordinates updated successfully for {gc_code}")
    else:
        raise Exception(f"Failed to update coordinates for {gc_code}")


def get_geocaches_from_list(session, list_code):
    def _transfer_cookies_to_selenium(session, driver):
        driver.delete_all_cookies()

        for cookie in session.cookies:
            driver.add_cookie({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': cookie.secure,
            })

    uri = f"{URLS["list"]}/{list_code}"

    service = webdriver.chrome.service.Service()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(_BASE_URL)

    _transfer_cookies_to_selenium(session, driver)

    driver.get(uri)

    # Wait for the page to load and find the necessary elements
    driver.implicitly_wait(3)

    # Extract the page source
    page_source = driver.page_source

    # Close the browser
    driver.quit()

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    gc_codes = []

    for div in soup.find_all("div", class_="geocache-meta"):
        spans = div.find_all("span")
        
        if len(spans) != 2:
            raise Exception("Sanity check failed: spans should equal 2")
        
        gc_code = spans[1].text.strip()
        gc_codes.append(gc_code)

    return gc_codes
