import re
import time
from datetime import datetime
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone

from results.models import DrawResult


class Command(BaseCommand):
    help = "Scrape lottery draw results from za.national-lottery.com and store in DB."

    GAMES = [
        # (game_slug_in_url, game_key, earliest_year)
        ("lotto",          "lotto",          2000),
        ("lotto-plus-1",   "lotto-plus-1",   2003),
        ("lotto-plus-2",   "lotto-plus-2",   2017),
        ("powerball",      "powerball",      2009),
        ("powerball-plus", "powerball-plus", 2010),
        ("daily-lotto",    "daily",          2019),
    ]

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    # Matches href like "/lotto/results/25-march-2026"
    DATE_HREF_RE = re.compile(r"/results/(\d{1,2})-([a-z]+)-(\d{4})")

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, default=None,
                            help="Scrape only this year (default: current year + last 4).")
        parser.add_argument("--all", action="store_true",
                            help="Scrape full history (slow).")

    def handle(self, *args, **opts):
        if opts["year"]:
            years = [opts["year"]]
        elif opts["all"]:
            years = list(range(2026, 1999, -1))
        else:
            years = list(range(timezone.now().year, timezone.now().year - 5, -1))

        total_saved = 0
        for slug, key, earliest in self.GAMES:
            saved = self._scrape_game(slug, key, years, earliest)
            total_saved += saved
            self.stdout.write(self.style.SUCCESS(f"  {slug}: {saved} new draws saved"))

        self.stdout.write(self.style.SUCCESS(f"\nTotal new draws: {total_saved}"))

    def _scrape_game(self, slug, key, years, earliest):
        saved = 0
        for year in years:
            if year < earliest:
                continue
            url = f"https://za.national-lottery.com/{slug}/results/{year}-archive"
            try:
                req = Request(url, headers=self.HEADERS)
                with urlopen(req, timeout=15) as response:
                    html = response.read().decode("utf-8", errors="replace")
            except Exception as exc:
                self.stderr.write(f"    [{slug} {year}] fetch failed: {exc}")
                continue

            soup = BeautifulSoup(html, "html.parser")
            rows = soup.find_all("tr")
            for row in rows:
                saved += self._parse_row(row, key)

            time.sleep(0.2)
        return saved

    def _parse_row(self, row, game_key):
        balls_ul = row.find("ul", class_="balls")
        if not balls_ul:
            return 0

        # Find the anchor whose href contains /results/<date>
        link = balls_ul.find_previous("a", href=self.DATE_HREF_RE)
        if not link:
            return 0

        match = self.DATE_HREF_RE.search(link["href"])
        if not match:
            return 0

        day, month_name, year = match.groups()
        draw_date = self._parse_date(day, month_name, year)
        if not draw_date:
            return 0

        balls = balls_ul.find_all("li", class_="ball")
        try:
            nums = [int(b.get_text(strip=True)) for b in balls]
        except ValueError:
            return 0

        if len(nums) < 5:
            return 0

        # Bonus ball is marked by class "bonus-ball" on one of the <li>s
        bonus = None
        mains = []
        for b in balls:
            classes = b.get("class", [])
            val = int(b.get_text(strip=True))
            if "bonus-ball" in classes:
                bonus = val
            else:
                mains.append(val)

        # Pad mains to 6 for the model
        padded = mains + [None] * (6 - len(mains))

        DrawResult.objects.update_or_create(
            game=game_key,
            draw_date=draw_date,
            defaults={
                "main_1": padded[0],
                "main_2": padded[1],
                "main_3": padded[2],
                "main_4": padded[3],
                "main_5": padded[4],
                "main_6": padded[5],
                "bonus_ball": bonus,
            },
        )
        return 1

    @staticmethod
    def _parse_date(day, month_name, year):
        try:
            return datetime.strptime(
                f"{day} {month_name} {year}", "%d %B %Y"
            ).date()
        except ValueError:
            try:
                return datetime.strptime(
                    f"{day} {month_name} {year}", "%d %b %Y"
                ).date()
            except ValueError:
                return None