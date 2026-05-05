# eBay E2E Automation Project

This project provides an automated E2E testing suite for the eBay shopping flow, built using **Python**, **Pytest**, and **Playwright**.

It is designed with scalability, maintainability, and clarity in mind, following modern automation best practices.

---

## Project Architecture

The project follows the **Page Object Model** design pattern, ensuring:

* Clear separation between test logic and UI interactions
* High code reusability
* Easier maintenance and scalability

### Directory Structure


pages/     # Page classes (BasePage, SearchPage, ItemPage, CartPage, LoginPage)
tests/     # Test files (e.g., test_ebay_flow.py)
data/      # Test data (JSON files for data-driven testing)
config/    # Environment configurations and base URLs
utils/     # Shared helpers and utility functions

---

## Getting Started

### Prerequisites

* Python 3.9+
* pip (Python package manager)

---

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/shakedshafsha/ebay-automations.git
cd <EBAY-AUTOMATIONS>
```

2. **Create and activate a virtual environment**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers**

```bash
playwright install
```

---

## Running Tests

### Run all tests (headless mode)

```bash
pytest
```

### Run tests with browser UI (headed mode)

```bash
pytest --headed
```

### Generate HTML report

```bash
pytest --html=report.html
```

---

## Assumptions and Limitations

* **Guest Access (Login Stub)**
  Tests run as a guest user to avoid CAPTCHA and anti-bot mechanisms. No login flow is executed.

* **Currency Handling**
  Prices may appear in different currencies (e.g., USD / ILS) depending on IP location.
  The framework validates values generically rather than relying on a fixed currency.

* **Environment**
  Tests are executed against the **eBay production environment**.

* **Dynamic UI**
  eBay frequently updates its UI. While stable selectors are used, significant UI changes may require updates in the `pages/` directory.

---

## Design Highlights

* Page Object Model (POM)
* Data-Driven Testing via JSON
* Separation of concerns (tests vs. logic)
* Scalable and maintainable structure
* Playwright best practices (auto-waits, locators, stability)

---

## Notes

This project is intended as a demonstration of E2E automation skills, including:

* UI test design
* Framework architecture
* Handling real-world challenges (dynamic UI, flaky behavior, environment differences)

---
