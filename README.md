# eBay E2E Automation

End-to-End test suite for the eBay shopping flow, built with **Python**, **Pytest**, and **Playwright**.

---

## Test Scenario

1. **Login** to eBay with credentials from the test data file (currently running as guest — login is commented out)
2. **Search** for items by keyword
3. **Filter** results by a maximum price
4. **Collect** up to 5 item URLs that fall within the price range
5. **Clear** the cart to start from a clean state
6. **Add** each collected item to the cart and record its price
7. **Assert** that the sum of the added item prices does not exceed the allowed budget (`max_price × items_count`)

### Pass Criteria

The test passes if:

```
sum(individual item prices) ≤ max_price × number_of_items
```

---

## Design Principles

| Principle | How it is applied |
|---|---|
| **POM** (Page Object Model) | Each page has its own class in `pages/`. Tests interact only through page objects, never with raw selectors. |
| **OOP** | All page classes inherit from `BasePage`, which provides `navigate()` and `take_screenshot()`. |
| **SRP** | Each class owns exactly one responsibility: `SearchPage` finds items, `ItemPage` adds them to cart, `CartPage` validates the total, `LoginPage` handles authentication. |
| **Data-Driven** | Test inputs (query, price limit, credentials) live in `data/search_data.json` and are injected via `@pytest.mark.parametrize`. |

---

## Project Structure

```
ebay-automations/
├── pages/
│   ├── base_page.py      # Shared page utilities (navigate, screenshot)
│   ├── login_page.py     # Login / session management
│   ├── search_page.py    # Search bar, price filter, result collection
│   ├── item_page.py      # Item detail page, variation selection, add-to-cart
│   └── cart_page.py      # Cart clearing and total validation
├── tests/
│   └── test_ebay_flow.py # Single parametrised E2E test
├── data/
│   └── search_data.json  # Test input: query, max_price, items_limit, credentials
├── config/
│   ├── urls.py           # Base URLs (home, cart, sign-in)
│   └── conftest.py       # (unused — root conftest.py is active)
├── utils/
│   └── helpers.py        # load_test_data(), extract_price()
├── screenshots/          # Auto-created; debug and result screenshots saved here
├── conftest.py           # Browser context config (viewport 1280×720)
├── pytest.ini            # pythonpath = . so packages resolve correctly
└── requirements.txt      # Python dependencies
```

---

## Test Data

Edit `data/search_data.json` to change the search scenario:

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

Multiple objects in the array produce one test case each.

---

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# 1. Clone
git clone https://github.com/shakedshafsha/ebay-automations.git
cd ebay-automations

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers
playwright install
```

---

## Running Tests

```bash
# Headless (default)
pytest

# With visible browser
pytest --headed

# Generate an HTML report
pytest --html=report.html

# Run only Chromium
pytest --browser chromium
```

Screenshots are saved automatically to `screenshots/` on every run.

---

## Limitations

- **Guest cart behaviour** — eBay's guest cart does not persist items reliably across page navigations. For full cart-total validation against the eBay-displayed subtotal, login must be enabled in `tests/test_ebay_flow.py`.
- **Dynamic UI** — eBay updates its selectors periodically. If tests break, check `pages/` for outdated CSS selectors.
- **CAPTCHA / 2FA** — Automated login may be blocked by eBay's bot-detection. Run tests during off-peak hours or use a dedicated test account.
- **Currency** — Prices are extracted as plain numbers; currency symbols are stripped to keep comparisons locale-independent.
