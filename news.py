import os
import re
import html
import hashlib
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

STYLE = {
    "World": ("🌍", "The planet remains eventful. Shocking, we know."),
    "Trending": ("🔥", "Everyone is talking about these. Allegedly."),
    "Tech": ("🤖", "Someone built something. Again."),
    "Entertainment": ("🎬", "Important news for people who have time."),
}

QUIPS = [
    "Shocking. Truly.",
    "Well, that's one way to start the day.",
    "We'll pretend we're surprised.",
    "Anyway.",
    "Sure, why not.",
    "Plot twist, apparently.",
    "Stay calm and read on.",
    "Wow. Okay.",
    "Add it to the pile.",
    "Big if true.",
]

# No jokes on serious stories
SERIOUS = re.compile(
    r"kill|dead|death|\bdie|shoot|attack|\bwar\b|bomb|crash|victim|disaster|"
    r"earthquake|flood|hostage|terror|murder|abuse|suicide|missing|injur|"
    r"tragedy|wildfire|hurricane|famine|massacre",
    re.I,
)

PER_FEED = 4  # stories per feed


def clean(text, limit):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "..."
    return text


def quip_for(title, snippet):
    if SERIOUS.search(title + " " + snippet):
        return ""
    n = int(hashlib.md5(title.encode()).hexdigest(), 16) % len(QUIPS)
    return f'<p class="q"><em>{html.escape(QUIPS[n])}</em></p>'


sections = []
for category, urls in FEEDS.items():
    emoji, intro = STYLE[category]
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
                    f"<h3>{emoji} {html.escape(title)}</h3>"
                    f"<p>{html.escape(snippet)}</p>"
                    f"{quip_for(title, snippet)}"
                    f'<a href="{html.escape(entry.link)}">'
                    f"Read on {html.escape(source or 'source')}</a>"
                    "</article>"
                )
        except Exception as e:
            print(f"Skipped {url}: {e}")
    if cards:
        sections.append(
            f"<h2>{emoji} {html.escape(category)}</h2>"
            f'<p class="intro">{html.escape(intro)}</p>' + "".join(cards)
        )

today = datetime.date.today().isoformat()
page = f"""<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Daily News (Sarcasm Included)</title>
<style>
body{{font-family:sans-serif;max-width:700px;margin:auto;padding:16px;line-height:1.5}}
article{{margin:16px 0;padding-bottom:12px;border-bottom:1px solid #ccc}}
h3{{margin:0 0 4px}}
.intro{{color:#666;font-style:italic}}
.q{{color:#b45309;margin:4px 0}}
</style></head><body>
<h1>Daily News, Sarcasm Included</h1>
<p>Real headlines, questionable commentary. Updated {today}.
Headlines link to the original sources.</p>
{''.join(sections)}
</body></html>"""

os.makedirs("docs", exist_ok=True)
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(page)
print("Done")
