import os
import re
import html
import datetime

import feedparser
import anthropic

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
PER_FEED = 3  # stories per feed

client = anthropic.Anthropic(api_key=os.environ["AI_API_KEY"])


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return html.unescape(re.sub(r"\s+", " ", text)).strip()[:500]


def summarize(title, snippet):
    prompt = (
        "Write a catchy but accurate headline and a 2-sentence summary in your "
        "own words, based ONLY on the info below. Do not add facts or guess. "
        "Reply with the headline on the first line and the summary on the "
        "second line, nothing else.\n\n"
        f"Title: {title}\nInfo: {snippet}"
    )
    msg = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    lines = [l.strip() for l in msg.content[0].text.strip().split("\n") if l.strip()]
    headline = lines[0] if lines else title
    summary = " ".join(lines[1:]) if len(lines) > 1 else ""
    return headline, summary


sections = []
for category, urls in FEEDS.items():
    cards = []
    for url in urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:PER_FEED]:
                title = clean(entry.get("title"))
                snippet = clean(entry.get("summary"))
                headline, summary = summarize(title, snippet)
                cards.append(
                    "<article>"
                    f"<h3>{html.escape(headline)}</h3>"
                    f"<p>{html.escape(summary)}</p>"
                    f'<a href="{html.escape(entry.link)}">Read the original</a>'
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
<h1>Daily News</h1><p>Updated {today}. Summaries are AI-written; check the source.</p>
{''.join(sections)}
</body></html>"""

os.makedirs("docs", exist_ok=True)
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(page)
print("Done")
