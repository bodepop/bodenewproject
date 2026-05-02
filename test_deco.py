"""Extract Deco data from the home page and client page."""
from deco_browser import DecoBrowser
import time

deco = DecoBrowser("192.168.2.1", "Ebunoluwa1/")
deco.start()

try:
    print("Logging in...")
    deco.login()
    print("Login OK!")

    # Get all API data from page load
    print("\nCapturing API data...")
    data = deco.get_all_data()
    print(f"Captured forms: {list(data.keys())}")
    for form, body in data.items():
        print(f"  {form}: {len(body)} bytes")

    # Now click on "Clients" link in the nav
    print("\nNavigating to Clients page...")
    try:
        deco.page.click('text=Clients', timeout=5000)
        time.sleep(4)
        deco.page.wait_for_load_state("networkidle")
    except Exception as e:
        print(f"  Click failed: {e}")
        # Try alternative
        try:
            deco.page.click(':text("Clients")', timeout=3000)
            time.sleep(4)
        except Exception:
            pass

    deco.page.screenshot(path="deco_clients.png")

    # Extract all visible text
    text = deco.page.evaluate("() => document.body.innerText")
    print(f"\nPage text:\n{text[:2000]}")

    # Extract structured data from DOM
    print("\n--- Extracting client entries ---")
    entries = deco.page.evaluate("""
        () => {
            const results = [];
            // Get all text nodes that look like device names or IPs
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            let node;
            while (node = walker.nextNode()) {
                const text = node.textContent.trim();
                if (text.length > 0 && text.length < 100) {
                    results.push(text);
                }
            }
            return results;
        }
    """)
    # Filter for interesting entries
    ips = [e for e in entries if '192.168.' in e]
    macs = [e for e in entries if len(e) == 17 and e.count('-') == 5]
    names = [e for e in entries if len(e) > 2 and len(e) < 40 and '192.168' not in e and '-' not in e[:5]]

    print(f"IPs found: {len(ips)}")
    for ip in ips[:30]:
        print(f"  {ip}")
    print(f"\nMACs found: {len(macs)}")
    for mac in macs[:10]:
        print(f"  {mac}")

finally:
    deco.stop()
    print("\nDone.")
