#!/usr/bin/env python3
"""Busca o calendário público de contribuições do GitHub sem token e salva em data/contributions.json."""

import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.getenv("GITHUB_USERNAME", "Gabriel-V-Mendes")
URL = f"https://github.com/users/{USERNAME}/contributions"


def parse_count(tooltip_text: str) -> int:
    if not tooltip_text or "No contributions" in tooltip_text:
        return 0
    m = re.search(r"(\d[\d,]*)\s+contribution", tooltip_text)
    return int(m.group(1).replace(",", "")) if m else 0


def fetch_contributions(username: str = USERNAME) -> dict:
    resp = requests.get(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "Mozilla/5.0 (compatible; ProfileHeatmapBot/1.0)"},
        timeout=20,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    tooltips = {}
    for tip in soup.find_all("tool-tip"):
        target_id = tip.get("for")
        if target_id:
            tooltips[target_id] = tip.get_text(strip=True)

    days = []
    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        date_str = cell["data-date"]
        level = int(cell.get("data-level", 0))
        cell_id = cell.get("id", "")
        count = parse_count(tooltips.get(cell_id, ""))
        if count == 0 and level > 0:
            # Fallback caso a estrutura do tooltip mude no HTML público
            count = level
        days.append({"date": date_str, "level": level, "count": count})

    days.sort(key=lambda d: d["date"])

    total = sum(d["count"] for d in days)
    heading = soup.select_one("h2#js-contribution-activity-description, h2.f4.text-normal")
    if heading:
        m = re.search(r"(\d[\d,]*)\s+contributions?", heading.get_text(" ", strip=True))
        if m:
            total = int(m.group(1).replace(",", ""))

    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        elif current_streak > 0:
            break

    best_day = max(days, key=lambda d: d["count"], default={"date": None, "count": 0})
    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    return {
        "username": username,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": dict(sorted(monthly.items())),
        "days": days,
    }


if __name__ == "__main__":
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    payload = fetch_contributions()
    out = data_dir / "contributions.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Salvo {len(payload['days'])} dias ({payload['total_contributions']} contribuições) em {out}")
