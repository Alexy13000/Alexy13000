"""GitHub GraphQL client: contribution calendar since account creation."""

from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from datetime import date, datetime, timezone

API = "https://api.github.com/graphql"

QUERY_USER = "query($login:String!){user(login:$login){createdAt}}"
QUERY_YEAR = """
query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){
    contributionsCollection(from:$from,to:$to){
      contributionCalendar{
        weeks{contributionDays{date contributionCount}}
      }
    }
  }
}"""

def token() -> str:
    """GITHUB_TOKEN in CI, otherwise the local `gh` CLI session."""
    value = os.environ.get("GITHUB_TOKEN", "").strip()
    if value:
        return value
    try:
        value = subprocess.run(["gh", "auth", "token"], check=True,
                               capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        value = ""
    if not value:
        raise SystemExit("No token: set GITHUB_TOKEN or run `gh auth login`.")
    return value


def _graphql(query: str, variables: dict, auth: str) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode()
    request = urllib.request.Request(API, data=body, headers={
        "Authorization": f"bearer {auth}",
        "Content-Type": "application/json",
        "User-Agent": "profilegen",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"][0].get("message", "GraphQL error"))
    return payload["data"]


def fetch(login: str, now: datetime) -> dict:
    """Return {"created": iso date, "days": {iso date: count}}.

    One request per calendar year, from the account creation to `now`.
    """
    auth = token()
    created = datetime.fromisoformat(
        _graphql(QUERY_USER, {"login": login}, auth)["user"]["createdAt"]
        .replace("Z", "+00:00"))
    now = now.astimezone(timezone.utc)
    days: dict[str, int] = {}
    for year in range(created.year, now.year + 1):
        start = max(created, datetime(year, 1, 1, tzinfo=timezone.utc))
        end = min(now, datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc))
        data = _graphql(QUERY_YEAR, {
            "login": login,
            "from": start.isoformat().replace("+00:00", "Z"),
            "to": end.isoformat().replace("+00:00", "Z"),
        }, auth)
        calendar = data["user"]["contributionsCollection"]["contributionCalendar"]
        for week in calendar["weeks"]:
            for day in week["contributionDays"]:
                days[day["date"]] = day["contributionCount"]
    return {"created": created.date().isoformat(), "days": days}


def parse_days(raw: dict) -> tuple[date, dict[date, int]]:
    """Turn the JSON payload into (creation date, {date: count})."""
    days = {date.fromisoformat(k): int(v) for k, v in raw["days"].items()}
    return date.fromisoformat(raw["created"]), days
