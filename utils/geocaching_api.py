import json
import os
import requests

from bs4 import BeautifulSoup

def get_session():
    session = requests.Session()

    # Login geocaching.com
    login_page_req = session.request(method="GET", url="https://www.geocaching.com/account/signin")
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

    after_login_page = session.request(method="POST", url="https://www.geocaching.com/account/signin", data=post)

    if "Sign out" in after_login_page.text:
        print("Login successful")
    else:
        raise Exception("Login failed")

    return {"session": session, "allow_clipboard": allow_clipboard}
