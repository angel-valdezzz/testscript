"""Validate the public runner configuration without importing browser providers."""

BROWSERS = {
    "playwright": {"chromium", "chrome", "edge", "firefox", "webkit"},
    "selenium": {"chrome", "edge", "firefox"},
}


def validate_config(config):
    allowed = {
        "provider", "browser", "headless", "incognito", "viewport_width", "viewport_height",
        "maximize", "timeout", "base_url", "output", "tests_use_flows_only",
    }
    unknown = set(config) - allowed
    if unknown:
        raise ValueError(f"Unknown configuration: {', '.join(sorted(unknown))}")
    provider = config.get("provider", "playwright")
    if not isinstance(provider, str) or provider not in BROWSERS:
        raise ValueError("provider must be playwright or selenium")
    browser = config.get("browser", "chromium" if provider == "playwright" else "chrome")
    if not isinstance(browser, str) or browser not in BROWSERS[provider]:
        raise ValueError(f"browser '{browser}' is unavailable for {provider}; choose {', '.join(sorted(BROWSERS[provider]))}")
    for key in ("headless", "incognito", "maximize", "tests_use_flows_only"):
        if key in config and not isinstance(config[key], bool):
            raise ValueError(f"{key} must be Bool")
    for key in ("viewport_width", "viewport_height"):
        value = config.get(key, 1440 if key == "viewport_width" else 900)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{key} must be a positive Int")
    timeout = config.get("timeout", 10)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
        raise ValueError("timeout must be a positive number of seconds")
    for key in ("base_url", "output"):
        if key in config and not isinstance(config[key], str):
            raise ValueError(f"{key} must be String")
    if config.get("maximize", False):
        if config.get("headless", True):
            raise ValueError("maximize requires headless = false (or --headed)")
        if any(key in config for key in ("viewport_width", "viewport_height")):
            raise ValueError("maximize cannot be combined with an explicit viewport size")
        if provider == "playwright" and browser in {"firefox", "webkit"}:
            raise ValueError("maximize is only supported for Chromium/Chrome/Edge with Playwright")
    return config
