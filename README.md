# eBay E2E Automation

End-to-End test suite for the eBay shopping flow, built with **Python**, **Pytest**, and **Playwright**.  
Follows **Page Object Model (POM)**, **OOP**, and **Single Responsibility Principle (SRP)**.

---

## Test Flow

| Step | Action | Implementation |
|------|--------|----------------|
| 1 | Open eBay and search for a product by keyword | `SearchPage.search()` |
| 2 | Apply a maximum-price filter to narrow results | `SearchPage.apply_max_price_filter()` |
| 3 | Collect up to 5 item URLs whose price ≤ `max_price` — follows pagination if needed | `SearchPage.collect_items_with_paging()` |
| 4 | Clear the cart to start from a clean state | `CartPage.clear_cart()` |
| 5 | Visit each item page, select random variants (size / color), click **Add to Cart**, save a screenshot | `ItemPage.add_items_to_cart()` |
| 6 | Open the cart, read the displayed total, assert it does not exceed the budget | `CartPage.assert_cart_total_not_exceeds()` |

### Pass Criteria

```
cart_displayed_total  ≤  max_price × number_of_items_added
```

The test reads the total **directly from eBay's cart page** (not from the prices collected during search).  
It passes when eBay's displayed cart total is within the expected budget.

---

## Architecture

### Design Principles

| Principle | How it is applied |
|-----------|-------------------|
| **POM** — Page Object Model | Every page has its own class in `pages/`. Tests call page methods; they never touch raw selectors or Playwright APIs directly. |
| **OOP** | All page classes inherit from `BasePage`, which provides `navigate()` and `take_screenshot()`. Locators and page-specific logic live in the relevant subclass. |
| **SRP** — Single Responsibility | `SearchPage` → find & filter items · `ItemPage` → add items to cart · `CartPage` → validate the total · `LoginPage` → session management · `BasePage` → shared browser utilities |
| **Data-Driven Testing** | Test inputs (search query, price cap, credentials) are stored in `data/search_data.json` and injected into the test via `@pytest.mark.parametrize`. Adding a new test case requires only a new JSON object — no code changes. |

### Class Diagram

```
BasePage
├── LoginPage    — sign-in, session detection
├── SearchPage   — open home, search, price filter, collect URLs, pagination
├── ItemPage     — visit item, variant selection, add-to-cart, screenshot
└── CartPage     — clear cart, read displayed total, assert budget
```

---

## Project Structure

```
ebay-automations/
│
├── pages/
│   ├── base_page.py       # navigate(), take_screenshot()
│   ├── login_page.py      # login(), ensure_logged_in(), is_logged_in()
│   ├── search_page.py     # search, price filter, URL collection, pagination
│   ├── item_page.py       # variant selection, add-to-cart, per-item screenshot
│   └── cart_page.py       # clear cart, read cart total, budget assertion
│
├── tests/
│   └── test_ebay_flow.py  # single parametrised E2E test
│
├── data/
│   └── search_data.json   # test inputs — one object per test case
│
├── config/
│   ├── urls.py            # EBAY_HOME_PAGE, EBAY_CART_PAGE, EBAY_SIGNIN_PAGE
│   └── conftest.py        # browser context settings (viewport 1280×720)
│
├── utils/
│   └── helpers.py         # load_test_data(), extract_price()
│
├── screenshots/           # auto-created; all screenshots are saved here
├── conftest.py            # root-level pytest fixtures
├── pytest.ini             # pythonpath = .  (makes packages importable)
└── requirements.txt       # Python dependencies
```

---

## Test Data

`data/search_data.json` drives the test. Each object becomes one parametrised test case.

```json
[
  {
    "search_query": "shoes",
    "max_price": 220,
    "items_limit": 5,
    "user_name": "your@email.com",
    "password": "yourPassword"
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `search_query` | string | Keyword to search on eBay |
| `max_price` | number | Maximum price per item (filter + budget cap) |
| `items_limit` | number | Maximum items to add (up to 5) |
| `user_name` | string | eBay account email |
| `password` | string | eBay account password |

---

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/shakedshafsha/ebay-automations.git
cd ebay-automations

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers
playwright install
```

---

## Running Tests

```bash
# Run all tests (headless)
pytest

# Run with a visible browser window
pytest --headed

# Run on a specific browser
pytest --browser chromium
pytest --browser firefox
pytest --browser webkit

# Generate an HTML report
pytest --html=report.html --self-contained-html
```

---

## Artifacts

Every test run produces the following files inside `screenshots/`:

| File | When created | Contents |
|------|-------------|----------|
| `item_1.png` … `item_N.png` | After each add-to-cart | The page state immediately after the item was added |
| `cart_debug.png` | Before the assertion | Full cart page — useful for debugging total-reading failures |
| `cart.png` | After the assertion | Final cart page state at assertion time |

---

## Known Limitations

- **Guest cart** — eBay's guest cart does not reliably persist items across page navigations. For stable cart-total validation, enable the login step in `tests/test_ebay_flow.py` (currently commented out).
- **CAPTCHA / 2FA** — Automated login may be challenged by eBay's bot-detection. Use a dedicated test account and run during off-peak hours.
- **Dynamic UI** — eBay periodically changes its HTML structure. If selectors break, update the relevant class in `pages/`.
- **Currency** — Prices are extracted as plain floats; currency symbols are stripped, so the suite works regardless of the locale eBay serves.
