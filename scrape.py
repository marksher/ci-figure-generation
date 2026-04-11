#!/usr/bin/env python3
"""
Crawl https://www.a16z.news/ for chart/graph images.

- Downloads articles containing charts into ./source/YYYY-MM/<slug>/
- Classifies each image with OpenAI o4-mini vision and saves to ./graphs/<type>/

Reads config from .env:
  OPENAI_API_KEY  — required
  MODEL           — defaults to o4-mini
"""

import os
import sys
import json
import time
import re
import base64
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import io

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()

DOMAIN = "https://www.a16z.news"
SITEMAP_URL = f"{DOMAIN}/sitemap.xml"
SOURCE_DIR = Path("source")
GRAPHS_DIR = Path("graphs")
CHART_TYPES = ["bar", "line", "pie", "scatter", "table", "other"]
MODEL = os.getenv("MODEL", "o4-mini")
DELAY_ARTICLE = 1.0   # seconds between article fetches
DELAY_IMAGE = 0.5     # seconds between image downloads

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; a16z-chart-library/1.0; +research)"
}

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def check_env():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("ERROR: OPENAI_API_KEY is not set.")
        print("Add it to .env or export it in your shell.")
        sys.exit(1)
    print(f"Model: {MODEL}")
    return key


def setup_dirs():
    SOURCE_DIR.mkdir(exist_ok=True)
    GRAPHS_DIR.mkdir(exist_ok=True)
    for t in CHART_TYPES:
        (GRAPHS_DIR / t).mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Step 1: Enumerate articles from sitemap
# ---------------------------------------------------------------------------

def get_article_urls():
    print(f"Fetching sitemap: {SITEMAP_URL}")
    resp = requests.get(SITEMAP_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "lxml-xml")
    urls = []
    for loc in soup.find_all("loc"):
        url = loc.text.strip()
        if "/p/" in url:
            urls.append(url)
    print(f"Found {len(urls)} article URLs")
    return urls


# ---------------------------------------------------------------------------
# Step 2 & 3: Fetch article, extract images, save to source/
# ---------------------------------------------------------------------------

def slug_from_url(url):
    path = urlparse(url).path  # e.g. /p/some-article-slug
    return path.rstrip("/").split("/")[-1]


def get_publish_date(soup):
    """Extract YYYY-MM from article metadata."""
    meta = soup.find("meta", property="article:published_time")
    if meta and meta.get("content"):
        return meta["content"][:7]  # YYYY-MM
    time_tag = soup.find("time")
    if time_tag and time_tag.get("datetime"):
        return time_tag["datetime"][:7]
    return "unknown"


def extract_body_images(soup):
    """
    Return substackcdn image URLs from the article body.
    Skips header/thumbnail images.
    """
    body = soup.find("div", class_="available-content")
    if not body:
        body = soup.find("article")
    if not body:
        return []

    imgs = []
    for img in body.find_all("img"):
        src = img.get("src", "")
        if "substackcdn.com" in src and "/fetch/" in src:
            # Strip query params for full-res URL
            clean = re.sub(r"\?.*$", "", src)
            if clean not in imgs:
                imgs.append(clean)

    return imgs


def save_article(article_dir: Path, url: str, html: str, pub_date: str, image_urls: list):
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "index.html").write_text(html, encoding="utf-8")
    meta = {
        "url": url,
        "published": pub_date,
        "image_urls": image_urls,
    }
    (article_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Step 4: Download + classify images with OpenAI o4-mini vision
# ---------------------------------------------------------------------------

def download_image(url: str) -> bytes | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"    [WARN] Failed to download {url}: {e}")
        return None


def classify_image(client: OpenAI, image_bytes: bytes) -> str:
    """
    Ask o4-mini to classify the image.
    Returns one of: bar, line, pie, scatter, table, other, skip
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.standard_b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"    [WARN] Could not process image: {e}")
        return "skip"

    prompt = (
        "Look at this image carefully.\n\n"
        "Is it a data chart or graph (bar chart, line chart, pie chart, scatter plot, "
        "data table, or similar data visualization)?\n\n"
        "If YES, reply with exactly ONE word from this list: bar, line, pie, scatter, table, other\n"
        "If NO (it's a photo, illustration, logo, avatar, decorative image, etc.), "
        "reply with exactly one word: skip\n\n"
        "Reply with one word only. No explanation."
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_completion_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64}",
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        result = response.choices[0].message.content.strip().lower()
        if result in CHART_TYPES:
            return result
        if result == "skip":
            return "skip"
        for t in CHART_TYPES:
            if t in result:
                return t
        return "other"
    except Exception as e:
        print(f"    [WARN] OpenAI API error: {e}")
        return "skip"


def save_graph(image_bytes: bytes, chart_type: str, slug: str, idx: int):
    filename = f"{slug}-{idx}.png"
    dest = GRAPHS_DIR / chart_type / filename
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.save(dest, format="PNG")
    except Exception as e:
        print(f"    [WARN] Could not save image {filename}: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    api_key = check_env()
    setup_dirs()
    client = OpenAI(api_key=api_key)

    article_urls = get_article_urls()

    stats = {
        "scanned": 0,
        "with_charts": 0,
        "skipped_no_images": 0,
        "errors": 0,
        "images_by_type": {t: 0 for t in CHART_TYPES},
    }

    for i, url in enumerate(article_urls, 1):
        slug = slug_from_url(url)
        print(f"\n[{i}/{len(article_urls)}] {slug}")

        # Check cache
        cached_dirs = list(SOURCE_DIR.glob(f"*/{slug}"))
        if cached_dirs:
            print(f"  Cached — loading from {cached_dirs[0]}")
            meta_path = cached_dirs[0] / "metadata.json"
            if meta_path.exists():
                meta = json.loads(meta_path.read_text())
                image_urls = meta.get("image_urls", [])
            else:
                image_urls = []
        else:
            # Fetch article
            try:
                resp = requests.get(url, headers=HEADERS, timeout=30)
                resp.raise_for_status()
                html = resp.text
            except Exception as e:
                print(f"  [ERROR] {e}")
                stats["errors"] += 1
                time.sleep(DELAY_ARTICLE)
                continue

            soup = BeautifulSoup(html, "lxml")
            image_urls = extract_body_images(soup)
            pub_date = get_publish_date(soup)

            if not image_urls:
                print("  No body images — skipping")
                stats["skipped_no_images"] += 1
                time.sleep(DELAY_ARTICLE)
                continue

            article_dir = SOURCE_DIR / pub_date / slug
            save_article(article_dir, url, html, pub_date, image_urls)
            print(f"  Saved article → source/{pub_date}/{slug}/ ({len(image_urls)} images)")
            time.sleep(DELAY_ARTICLE)

        stats["scanned"] += 1

        if not image_urls:
            stats["skipped_no_images"] += 1
            continue

        # Classify each image
        article_had_chart = False
        for j, img_url in enumerate(image_urls, 1):
            print(f"  Image {j}/{len(image_urls)}: ", end="", flush=True)
            image_bytes = download_image(img_url)
            time.sleep(DELAY_IMAGE)
            if not image_bytes:
                print("download failed")
                continue

            chart_type = classify_image(client, image_bytes)
            print(chart_type)

            if chart_type != "skip":
                save_graph(image_bytes, chart_type, slug, j)
                stats["images_by_type"][chart_type] += 1
                article_had_chart = True

        if article_had_chart:
            stats["with_charts"] += 1

    # Summary
    print("\n" + "=" * 50)
    print("DONE")
    print(f"Articles scanned:       {stats['scanned']}")
    print(f"Articles with charts:   {stats['with_charts']}")
    print(f"Skipped (no images):    {stats['skipped_no_images']}")
    print(f"Errors:                 {stats['errors']}")
    print("Charts saved by type:")
    for t, n in stats["images_by_type"].items():
        if n:
            print(f"  {t:10s}: {n}")
    total = sum(stats["images_by_type"].values())
    print(f"  {'TOTAL':10s}: {total}")


if __name__ == "__main__":
    main()
