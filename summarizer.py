import requests
import feedparser

url = "https://sapo.pt/rss/destaques"

response = requests.get(url)
feed = feedparser.parse(response.content)

# Convert RSS feed entries to Markdown format for LLM processing
def rss_to_markdown(feed):
    md = ""
    for entry in feed.entries:
        md += f"## {entry.title}\n"
        if hasattr(entry, "published"):
            md += f"*Published:* {entry.published}\n"
        if hasattr(entry, "link"):
            md += f"[Read more]({entry.link})\n"
        if hasattr(entry, "summary"):
            md += f"\n{entry.summary}\n"
        md += "\n---\n"
    return md

markdown_feed = rss_to_markdown(feed)
print(markdown_feed)
