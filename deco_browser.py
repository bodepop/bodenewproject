"""
TP-Link Deco data fetcher using Playwright headless browser.
Logs in via the web admin and extracts client/device data from the page.
"""
from playwright.sync_api import sync_playwright
import time
import json
import re


class DecoBrowser:
    def __init__(self, host, password):
        self.host = f"https://{host}" if not host.startswith("http") else host
        self.password = password
        self.pw = None
        self.browser = None
        self.page = None

    def start(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=True)
        self.page = self.browser.new_page(ignore_https_errors=True)

    def stop(self):
        if self.browser:
            self.browser.close()
        if self.pw:
            self.pw.stop()

    def login(self):
        self.page.goto(f"{self.host}/webpages/index.html", wait_until="networkidle")
        time.sleep(2)
        self.page.fill('input[type="password"]', self.password)
        time.sleep(1)
        self.page.click('a.button-button:has-text("LOG IN")')
        time.sleep(5)
        self.page.wait_for_load_state("networkidle")
        return "Home" in self.page.title() or "home" in self.page.title().lower()

    def get_all_data(self):
        """Reload page and capture all API responses."""
        responses = {}

        def capture(response):
            if "/cgi-bin/luci" in response.url and response.status == 200:
                # Extract the form name from URL
                url = response.url
                for form in ["client_list", "device_list", "wlan", "wan_ipv4", "lan_ip", "mode"]:
                    if form in url:
                        try:
                            responses[form] = response.text()
                        except Exception:
                            pass

        self.page.on("response", capture)
        self.page.reload(wait_until="networkidle")
        time.sleep(5)
        self.page.remove_listener("response", capture)
        return responses

    def get_page_info(self):
        """Extract visible info directly from the rendered page."""
        return self.page.evaluate("""
            () => {
                const text = document.body.innerText;
                return {
                    title: document.title,
                    url: window.location.href,
                    text: text,
                };
            }
        """)

    def parse_clients_from_page(self):
        """Navigate to client list and extract data from the rendered page."""
        # Click on Clients section
        try:
            self.page.click('text=Clients', timeout=5000)
            time.sleep(3)
            self.page.wait_for_load_state("networkidle")
            time.sleep(2)
        except Exception:
            pass

        # Extract client data from the rendered page
        clients = self.page.evaluate("""
            () => {
                const clients = [];
                // Try to find client entries in the DOM
                const rows = document.querySelectorAll('[class*="client"], [class*="device-item"], tr, .list-item');
                for (const row of rows) {
                    const text = row.innerText;
                    if (text && text.includes('.') && text.length > 10) {
                        clients.push(text.trim());
                    }
                }
                // Also get the full page text for parsing
                return {
                    clients: clients,
                    fullText: document.body.innerText,
                };
            }
        """)
        return clients

    def navigate_to_clients(self):
        """Navigate to client page and capture the API response."""
        responses = []

        def capture(response):
            if "client_list" in response.url and response.status == 200:
                try:
                    responses.append(response.text())
                except Exception:
                    pass

        self.page.on("response", capture)

        # Try clicking on clients
        try:
            self.page.click('text=Clients', timeout=5000)
            time.sleep(3)
        except Exception:
            pass

        # Also try clicking on the client count
        try:
            els = self.page.query_selector_all('[class*="client"]')
            for el in els:
                if el.is_visible():
                    el.click()
                    time.sleep(2)
                    break
        except Exception:
            pass

        self.page.remove_listener("response", capture)
        return responses

    def get_screenshot(self, path="deco_screenshot.png"):
        self.page.screenshot(path=path)

    def block_device(self, device_name):
        """Block a device by clicking on it and using the block option."""
        try:
            # Navigate to clients
            self.page.click('text=Clients', timeout=5000)
            time.sleep(3)
            # Click on the device
            self.page.click(f'text={device_name}', timeout=5000)
            time.sleep(2)
            # Look for block button
            self.page.click('text=Block', timeout=5000)
            time.sleep(1)
            # Confirm
            try:
                self.page.click('text=YES', timeout=3000)
                time.sleep(2)
            except Exception:
                pass
            return True
        except Exception as e:
            return str(e)

    def unblock_device(self, device_name):
        """Unblock a device."""
        try:
            # Navigate to blocked clients
            self.page.click('text=Clients', timeout=5000)
            time.sleep(3)
            # Look for blocked devices section
            try:
                self.page.click('text=Blocked', timeout=3000)
                time.sleep(2)
            except Exception:
                pass
            self.page.click(f'text={device_name}', timeout=5000)
            time.sleep(2)
            self.page.click('text=Unblock', timeout=5000)
            time.sleep(1)
            try:
                self.page.click('text=YES', timeout=3000)
                time.sleep(2)
            except Exception:
                pass
            return True
        except Exception as e:
            return str(e)
