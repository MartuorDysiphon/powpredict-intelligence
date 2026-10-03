# Powpredict Intelligence

Lottery draw archival, statistical analysis, and pattern-matched number set generation for South African and UK lottery games.

---

## Tech Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend & Core** | **Python 3.10+** | Powers backend logic, predictive scoring engines, and data processing. |
| | **Django** | High-level web framework structuring modular applications and routing. |
| **Database** | **SQLite** | Serverless SQL database storing historical draws and local predictions. |
| **Scraping & APIs** | **BeautifulSoup4** | HTML and XML parsing engine for extracting lottery draw archives. |
| | **urllib** | Native Python library for handling HTTP requests and URL fetching. |
| | **Open-Meteo** | External weather API supplying live meteorological context. |
| **Frontend** | **Vanilla JavaScript** | Native client-side scripting for interactive dashboards and countdowns. |
| | **Custom CSS** | Modular, component-driven stylesheets scoped per Django application. |
| **Deployment** | **Gunicorn** | Production-grade Python WSGI HTTP server. |
| | **WhiteNoise** | Efficient static asset serving directly through WSGI. |

---

## Features

*   **Dashboard**: Live draw counters, hot and cold number analytics, odd-even and low-high distribution splits, next draw countdown timers, and recent activity logs.
*   **Predictor Engine**: Fourteen-metric scoring algorithm evaluating over five hundred recent draws to generate five thousand candidate sets per run, complete with companion line generation, deep analysis panels, and live weather context.
*   **Results Archive**: Comprehensive historical records per game, automatically refreshed when stale.
*   **Analytics**: In-depth computation of hot numbers, cold numbers, and frequency distributions.
*   **History**: Local storage tracking past predictions with built-in text export capabilities.

---

## Supported Games

*   Lotto
*   Lotto Plus 1
*   Lotto Plus 2
*   PowerBall
*   PowerBall Plus
*   Daily Lotto
*   UK49s Lunchtime
*   UK49s Teatime

---

## Setup Instructions

```bash
git clone https://github.com/MartuorDysiphon/powpredict-intelligence.git
cd powpredict-intelligence

python -m venv .venv
.venv\Scripts\activate  # On macOS/Linux use: source .venv/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py scrape_results
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Management Commands

```bash
python manage.py scrape_results                # Scrape current year plus previous four years
python manage.py scrape_results --year 2024    # Scrape a single specified year
python manage.py scrape_results --all          # Scrape full historical archive
python manage.py migrate                       # Apply database migrations
python manage.py createsuperuser               # Create an administrative user account
```

---

## Project Structure

```text
core/           Shared templates, static assets, base stylesheet, and global JavaScript
dashboard/      Landing page featuring live database summaries and metrics
predictor/      Scoring engine, statistical analysis suite, and weather context integration
results/        Draw result database models and automated scraper management commands
analytics/      Hot and cold number computation engines and JSON analytics endpoints
history/        Local persistence layer for generated prediction history
```

*Note: Each page is isolated as its own modular Django app with dedicated templates, views, URLs, and CSS modules.*

---

## Technical Notes

*   All statistical computations are derived strictly from the local database.
*   The confidence score represents a mathematical match score against historical distribution shapes, not a probability of winning.
*   Lottery draws are entirely random and independent events.
*   Weather data integration is strictly for display context.

---

## Responsible Play

Gambling is intended for entertainment, not as a source of income. Help and support resources are available. Strictly restricted to individuals eighteen years or older.
