"""Build the profile: fetch contributions, render the SVG cards and README.

    python3 -m profilegen                 # fetch from GitHub, write assets/ + README.md
    python3 -m profilegen --cached        # reuse .cache/contributions.json
    python3 -m profilegen --demo          # synthetic busy year, written to .preview/
    python3 -m profilegen --demo --lang fr
"""

from __future__ import annotations

import argparse
import importlib
import json
import random
import sys
import tomllib
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from . import github
from .i18n import Formatter
from .readme import readme
from .theme import palette

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "contributions.json"
CARDS = ("header", "projects", "stack", "stats_card")
LIMIT_SVG = 300 * 1024


@dataclass
class Context:
    cfg: dict
    labels: dict
    fmt: Formatter
    now: datetime
    created: date
    days: dict

    @property
    def today(self) -> date:
        return self.now.date()

    def palette(self, theme: str) -> dict:
        return palette(theme)


def load_config(lang: str | None = None) -> tuple[dict, dict]:
    with open(ROOT / "profile.toml", "rb") as fh:
        cfg = tomllib.load(fh)
    if lang:
        cfg["lang"] = lang
    lang = cfg.get("lang", "en")
    if lang not in cfg:
        raise SystemExit(f'profile.toml: no [{lang}] block for lang = "{lang}"')
    return cfg, cfg[lang]


def demo_data(today: date) -> dict:
    """A plausible busy year, to judge the design with a full graph."""
    rng = random.Random(7)
    created = today - timedelta(days=500)
    days, d = {}, created
    while d <= today:
        weekend = d.weekday() >= 5
        quiet = rng.random() < (0.55 if weekend else 0.12)
        days[d.isoformat()] = 0 if quiet else rng.choice((1, 2, 3, 4, 6, 9, 14))
        d += timedelta(1)
    return {"created": created.isoformat(), "days": days}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="profilegen")
    parser.add_argument("--cached", action="store_true", help="use .cache/contributions.json")
    parser.add_argument("--demo", action="store_true", help="synthetic data, output to .preview/")
    parser.add_argument("--lang", help="override lang (with --demo only)")
    parser.add_argument("--only", help="comma-separated cards to render")
    args = parser.parse_args(argv)

    cfg, labels = load_config(args.lang if args.demo else None)
    now = datetime.now(ZoneInfo(cfg.get("timezone", "UTC")))

    if args.demo:
        raw = demo_data(now.date())
        out_dir = ROOT / ".preview"
    else:
        if args.cached and CACHE.exists():
            raw = json.loads(CACHE.read_text())
        else:
            raw = github.fetch(cfg["login"], now)
            CACHE.parent.mkdir(exist_ok=True)
            CACHE.write_text(json.dumps(raw, indent=1, sort_keys=True))
        out_dir = ROOT / "assets"
    created, days = github.parse_days(raw)

    ctx = Context(cfg, labels, Formatter(cfg.get("lang", "en"), labels["stats"]), now,
                  created, days)
    out_dir.mkdir(exist_ok=True)
    cards = args.only.split(",") if args.only else CARDS
    total = 0
    for name in cards:
        module = importlib.import_module(f".{name}", __package__)
        for theme in ("dark", "light"):
            svg = module.render(ctx, theme)
            target = out_dir / f"{name.removesuffix('_card')}-{theme}.svg"
            target.write_text(svg, encoding="utf-8")
            size = len(svg.encode())
            total += size
            flag = "  ⚠ over 300 KB" if size > LIMIT_SVG else ""
            print(f"{target.relative_to(ROOT)}  {size / 1024:6.1f} KB{flag}")
    print(f"total {total / 1024:.1f} KB")

    if not args.demo and not args.only:
        (ROOT / "README.md").write_text(readme(ctx), encoding="utf-8")
        print("README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
