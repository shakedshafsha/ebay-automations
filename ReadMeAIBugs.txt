## ReadMeAIBugs

Static code review of the provided automation script.
Below are all identified bugs, detailed explanations, and the corrected code.

---

## Identified Bugs

### Bug 1 — Improper Playwright Initialization (Resource Leak)

**Problem:**
The script starts Playwright with `sync_playwright().start()` but never calls `.stop()`.
If an exception is raised during the test, execution jumps past `browser.close()`,
leaving the browser process and the Playwright instance running in the background.

**Fix:**
Use the `with sync_playwright() as p:` context manager.
Python guarantees the block is exited cleanly — including on exceptions —
so both the browser and the Playwright process are always shut down correctly.

---

### Bug 2 — Hardcoded Sleeps (`time.sleep`)

**Problem:**
`time.sleep(2)` and `time.sleep(3)` are hardcoded delays. This is a well-known
anti-pattern in UI automation because:
- If the page loads slower than the sleep, the test fails intermittently (flaky).
- If the page loads faster, the test wastes time unconditionally.

**Fix:**
Remove the `time` import entirely. Playwright has built-in auto-waiting: every
action (`.fill()`, `.click()`) automatically waits for the target element to be
ready. For explicit waiting use `page.wait_for_selector()` or `expect(...).to_be_visible()`.

---

### Bug 3 — No Assertions (Not a Real Test)

**Problem:**
The function is called `test_search_functionality` but it never asserts anything.
`results = page.locator(".result-item")` only creates a locator object — it does
not verify that any results are actually present. The test passes even when the
search returns zero results or the page is completely broken.

**Fix:**
Use Playwright's `expect` API to assert that at least one result is visible after
the search action completes.

---

### Bug 4 — Unused Selenium Import

**Problem:**
`from selenium import webdriver` is imported but never referenced anywhere in the
script. Selenium and Playwright are separate frameworks; mixing their imports
creates confusion and adds an unnecessary dependency to the environment.

**Fix:**
Remove the import line.

---

## Corrected Code

```python
from playwright.sync_api import sync_playwright, expect


def test_search_functionality():
    # Bug 1 fixed: context manager guarantees cleanup even if an exception occurs
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto("https://example.com")

        # Bug 2 fixed: removed time.sleep(); Playwright auto-waits for elements
        search_box = page.locator("#search")
        search_box.fill("playwright testing")

        page.locator(".button").click()

        # Bug 3 fixed: assert that at least one result is visible
        results = page.locator(".result-item")
        expect(results.first).to_be_visible()
        assert results.count() > 0, "Expected search results but found none."

        # Bug 4 fixed: removed unused 'from selenium import webdriver'

        # browser and Playwright are automatically closed when the 'with' block exits
```
