"""Browser contract. Each test gets a fresh browser and automatic teardown."""

import os
from pathlib import Path
from time import monotonic, sleep
from typing import Protocol

from testscript.model import Locator


class BrowserAdapter(Protocol):
    def open(self, url: str): ...
    def click(self, locator: Locator): ...
    def type(self, locator: Locator, value: str): ...
    def select(self, locator: Locator, value: str): ...
    def check(self, locator: Locator): ...
    def text(self, locator: Locator) -> str: ...
    def value(self, locator: Locator) -> str: ...
    def visible(self, locator: Locator) -> bool: ...
    def screenshot(self, path: Path): ...
    def close(self): ...


class PlaywrightAdapter:
    def __init__(self, timeout=10, headless=True):
        from playwright.sync_api import sync_playwright

        self.owner = sync_playwright().start()
        try:
            launch = {"headless": headless}
            if os.getenv("TSCR_BROWSER_EXECUTABLE"):
                launch["executable_path"] = os.environ["TSCR_BROWSER_EXECUTABLE"]
            self.browser = self.owner.chromium.launch(**launch)
            self.page = self.browser.new_page(viewport={"width": 1440, "height": 900})
            self.page.set_default_timeout(timeout * 1000)
            self.page.set_default_navigation_timeout(timeout * 1000)
        except Exception:
            self.owner.stop()
            raise

    def locate(self, locator):
        if not isinstance(locator, Locator):
            raise TypeError("Expected css(...) or xpath(...) locator")
        return self.page.locator(f"{locator.strategy}={locator.value}")

    def open(self, url):
        self.page.goto(url)

    def click(self, locator):
        self.locate(locator).click()

    def type(self, locator, value):
        self.locate(locator).fill(str(value))

    def select(self, locator, value):
        self.locate(locator).select_option(str(value))

    def check(self, locator):
        self.locate(locator).check()

    def text(self, locator):
        return self.locate(locator).inner_text()

    def value(self, locator):
        return self.locate(locator).input_value()

    def visible(self, locator):
        self.locate(locator).wait_for(state="visible")
        return True

    def screenshot(self, path):
        self.page.screenshot(path=str(path), full_page=True)

    def close(self):
        try:
            self.browser.close()
        finally:
            self.owner.stop()


class SeleniumAdapter:
    def __init__(self, timeout=10, headless=True):
        from selenium import webdriver

        self.timeout = timeout
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1440,900")
        if os.getenv("TSCR_BROWSER_NO_SANDBOX") == "1":
            options.add_argument("--no-sandbox")
        if os.getenv("TSCR_BROWSER_EXECUTABLE"):
            options.binary_location = os.environ["TSCR_BROWSER_EXECUTABLE"]
        from selenium.webdriver.chrome.service import Service

        service = (
            Service(os.environ["TSCR_DRIVER_EXECUTABLE"]) if os.getenv("TSCR_DRIVER_EXECUTABLE") else None
        )
        self.driver = webdriver.Chrome(options=options, service=service)
        self.driver.set_page_load_timeout(timeout)

    def locate(self, locator, clickable=False):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as ec
        from selenium.webdriver.support.ui import WebDriverWait

        if not isinstance(locator, Locator):
            raise TypeError("Expected css(...) or xpath(...) locator")
        pair = (By.CSS_SELECTOR if locator.strategy == "css" else By.XPATH, locator.value)
        condition = ec.element_to_be_clickable if clickable else ec.visibility_of_element_located
        return WebDriverWait(self.driver, self.timeout).until(condition(pair))

    def open(self, url):
        self.driver.get(url)

    def click(self, locator):
        from selenium.common.exceptions import (
            ElementClickInterceptedException,
            StaleElementReferenceException,
        )

        deadline = monotonic() + self.timeout
        while True:
            try:
                self.locate(locator, clickable=True).click()
                return
            except (ElementClickInterceptedException, StaleElementReferenceException):
                if monotonic() >= deadline:
                    raise
                sleep(0.1)

    def type(self, locator, value):
        element = self.locate(locator, clickable=True)
        element.clear()
        element.send_keys(str(value))

    def select(self, locator, value):
        from selenium.webdriver.support.ui import Select

        Select(self.locate(locator)).select_by_value(str(value))

    def check(self, locator):
        element = self.locate(locator, clickable=True)
        if not element.is_selected():
            element.click()

    def text(self, locator):
        return self.locate(locator).text

    def value(self, locator):
        return self.locate(locator).get_attribute("value")

    def visible(self, locator):
        return self.locate(locator).is_displayed()

    def screenshot(self, path):
        if not self.driver.save_screenshot(str(path)):
            raise RuntimeError("Selenium could not save screenshot")

    def close(self):
        self.driver.quit()
