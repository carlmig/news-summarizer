import requests
import feedparser
from datetime import datetime
import os
from groq import Groq
from dotenv import load_dotenv


raw_prompt = """
    You are a curator for news and will select the news to show to the user, based on its interests. You will be given a list of INTERESTS and a list of NEWS and will provide a response 
    with the selected news following a specific TEMPLATE.
    If news don't fit the interests, then ignore it. If there are interests without news, ignore it.
    
    The INTERESTS are: {interests}.
    The TEMPLATE is:

    # <category emoji> <category>

    ---

    #### <title>

    <description of the news>  
    [Saber Mais](<link>)
    
    ---

    The NEWS are:

"""



# Read and parse an rss url
def read_rss(rss_url):
    response = requests.get(rss_url)
    return feedparser.parse(response.content)


# Convert RSS feed entries to Markdown format for LLM processing
def rss_to_markdown(entries):
    md = ""
    for entry in entries:
        md += f"## {entry.title}\n"
        if hasattr(entry, "published"):
            md += f"*Published:* {entry.published}\n"
        if hasattr(entry, "link"):
            md += f"[Read more]({entry.link})\n"
        if hasattr(entry, "summary"):
            md += f"\n{entry.summary}\n"
        md += "\n---\n"
    return md


# export markdown content to Hugo file
def export_hugo(content):
    # file path
    output_dir = "content/posts"
    os.makedirs(output_dir, exist_ok=True)

    with open("hugo.template", "r", encoding="utf-8") as r:
        template = r.read()

    frontmatter = template.format_map(
        {
            "date_simple": datetime.now().strftime("%Y-%m-%d"),
            "date_full": datetime.now(datetime.UTC).isoformat()
        }
    )

    filename = f"{datetime.now().strftime("%Y-%m-%d")}.md"
    filepath = os.path.join(output_dir, filename)

    # save file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter + content)    







def prepare_prompt(interests, news):
    prompt = raw_prompt.format_map(
        {"interests": interests}
    )
    return prompt + news




def call_llm(prompt):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    chat_completion = client.chat.completions.create(
       messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    return chat_completion.choices[0].message.content




def execute():
    load_dotenv()
    
    url = "https://sapo.pt/rss/destaques"
    feed = read_rss(url)

    max_news_limit = 50
    markdown_feed = rss_to_markdown(feed.entries[:max_news_limit])

    interests = "top world news, top portugal news, surprising science"
    prompt = prepare_prompt(interests, markdown_feed)

    print(prompt)
    response = call_llm(prompt)

    # save response to file
    export_hugo(response)


execute()

