# Powpredict Intelligence

A Django web app for lottery number analysis and set generation across major South African and UK lottery games. Uses frequency-weighted algorithms and deep statistical analysis over historical draw data.

## Features

- **Dashboard** — hot/cold numbers, odd/even and low/high splits, live draw schedule, latest draws
- **Predictor** — weighted set generation with companion lines, deep analysis panel, live weather context
- **Results** — full historical draw archive, auto-refreshed when stale
- **Analytics** — hot, cold and frequency distribution computed from the database
- **History** — locally stored predictions

## Supported games

- Lotto (South Africa)
- Lotto Plus 1 and Plus 2
- PowerBall and PowerBall Plus
- Daily Lotto
- UK49s Lunchtime and Teatime

## Stack

- Django 5+
- SQLite
- Custom CSS, no frameworks
- Vanilla JavaScript
- BeautifulSoup + urllib for scraping
- Open-Meteo for weather context

## Quick start

```bash
git clone https://github.com/MartuorDysiphon/powpredict-intelligence.git
cd powpredict-intelligence

python -m venv .venv
.venv\Scripts\activate         # Windows
source .venv/bin/activate      # macOS / Linux

pip install -r requirements.txt

python manage.py migrate
python manage.py scrape_results --year 2026
python manage.py runserver
