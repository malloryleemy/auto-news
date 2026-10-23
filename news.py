import os
import re
import html
import datetime

import feedparser

FEEDS = {
    "World": ["https://feeds.bbci.co.uk/news/rss.xml"],
    "Trending": ["https://news.google.com/rss"],
    "Tech": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
    ],
    "Entertainment": [
        "https://variety.com/feed/",
        "https://www.hollywoodreporter.com/feed/",
    ],
}
PER_FEED = 4  # stories per feed


def clean(text, limit):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "..."
    return text


sections = []
for category, urls in FEEDS.items():
    cards = []
    for url in urls:
        try:
            feed = feedparser.parse(url)
            source = clean(feed.feed.get("title", ""), 60)
            for entry in feed.entries[:PER_FEED]:
                title = clean(entry.get("title"), 200)
                snippet = clean(entry.get("summary"), 200)
                cards.append(
                    "<article>"
                    f"<h3>{html.escape(title)}</h3>"
                    f"<p>{html.escape(snippet)}</p>"
                    f'<a href="{html.escape(entry.link)}">'
                    f"Read on {html.escape(source or 'source')}</a>"
                    "</article>"
                )
        except Exception as e:
            print(f"Skipped {url}: {e}")
    if cards:
        sections.append(f"<h2>{html.escape(category)}</h2>" + "".join(cards))

today = datetime.date.today().isoformat()
page = f"""<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Daily News</title>
<style>
body{{font-family:sans-serif;max-width:700px;margin:auto;padding:16px;line-height:1.5}}
article{{margin:16px 0;padding-bottom:12px;border-bottom:1px solid #ccc}}
h3{{margin:0 0 4px}}
</style></head><body>
<h1>Daily News</h1><p>Updated {today}. Headlines link to the original sources.</p>
{''.join(sections)}
</body></html>"""

os.makedirs("docs", exist_ok=True)
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(page)
print("Done")
