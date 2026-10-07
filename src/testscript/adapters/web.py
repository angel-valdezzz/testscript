"""Browser contract. Each test gets a fresh browser and automatic teardown."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
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
    def __init__(self, timeout=10, headless=True, *, browser=None, incognito=True,
                 viewport_width=1440, viewport_height=900, maximize=False):
        from playwright.sync_api import sync_playwright

        self.owner = sync_playwright().start()
        self.browser, self.context, self.profile = None, None, None
        try:
            launch = {"headless": headless}
            browser = browser or "chromium"
            engine = getattr(self.owner, browser if browser in {"firefox", "webkit"} else "chromium")
            if browser in {"chrome", "edge"}:
                launch["channel"] = "chrome" if browser == "chrome" else "msedge"
            if maximize:
                launch["args"] = ["--start-maximized"]
            context = {"no_viewport": True} if maximize else {
                "viewport": {"width": viewport_width, "height": viewport_height}
            }
            if os.getenv("TSCR_BROWSER_EXECUTABLE"):
                launch["executable_path"] = os.environ["TSCR_BROWSER_EXECUTABLE"]
            if incognito:
                self.browser = engine.launch(**launch)
                self.context = self.browser.new_context(**context)
            else:
                self.profile = TemporaryDirectory(prefix="tscr-profile-")
                self.context = engine.launch_persistent_context(self.profile.name, **launch, **context)
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            self.page.set_default_timeout(timeout * 1000)
            self.page.set_default_navigation_timeout(timeout * 1000)
        except Exception:
            self.close()
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
            if self.context:
                self.context.close()
        finally:
            try:
                if self.browser:
                    self.browser.close()
            finally:
                self.owner.stop()
                if self.profile:
                    self.profile.cleanup()


class SeleniumAdapter:
    def __init__(self, timeout=10, headless=True, *, browser=None, incognito=True,
                 viewport_width=1440, viewport_height=900, maximize=False):
        from selenium import webdriver

        self.timeout = timeout
        browser = browser or "chrome"
        options_class, driver_class = {
            "chrome": (webdriver.ChromeOptions, webdriver.Chrome),
            "edge": (webdriver.EdgeOptions, webdriver.Edge),
            "firefox": (webdriver.FirefoxOptions, webdriver.Firefox),
        }[browser]
        options = options_class()
        if headless:
            options.add_argument("-headless" if browser == "firefox" else "--headless=new")
        if incognito:
            if browser == "firefox":
                options.set_preference("browser.privatebrowsing.autostart", True)
            else:
                options.add_argument("--incognito" if browser == "chrome" else "--inprivate")
        if os.getenv("TSCR_BROWSER_NO_SANDBOX") == "1" and browser != "firefox":
            options.add_argument("--no-sandbox")
        if os.getenv("TSCR_BROWSER_EXECUTABLE"):
            options.binary_location = os.environ["TSCR_BROWSER_EXECUTABLE"]
        if browser == "firefox":
            from selenium.webdriver.firefox.service import Service
        elif browser == "edge":
            from selenium.webdriver.edge.service import Service
        else:
            from selenium.webdriver.chrome.service import Service

        service = (
            Service(os.environ["TSCR_DRIVER_EXECUTABLE"]) if os.getenv("TSCR_DRIVER_EXECUTABLE") else None
        )
        self.driver = driver_class(options=options, service=service)
        try:
            self.driver.set_page_load_timeout(timeout)
            self.driver.get("about:blank")
            if maximize:
                self.driver.maximize_window()
            else:
                self.driver.set_window_size(viewport_width, viewport_height)
                for _ in range(2):
                    delta = self.driver.execute_script(
                        "return [window.outerWidth-window.innerWidth, window.outerHeight-window.innerHeight]"
                    )
                    self.driver.set_window_size(viewport_width + delta[0], viewport_height + delta[1])
                if headless and browser in {"chrome", "edge"}:
                    self.driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
                        "width": viewport_width, "height": viewport_height,
                        "deviceScaleFactor": 1, "mobile": False,
                    })
        except Exception:
            self.driver.quit()
            raise

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
