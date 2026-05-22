import requests

USERNAME = "DebanKsahu"
README_PATH = "README.md"


def fetch_prs():
    url = f"https://api.github.com/search/issues?q=author:{USERNAME}+type:pr+state:open"
    data = requests.get(url).json()
    return data.get("items", [])


def fetch_issues():
    url = f"https://api.github.com/search/issues?q=author:{USERNAME}+type:issue+state:open"
    data = requests.get(url).json()
    return data.get("items", [])


def format_items(items, limit=10):
    lines = []
    for item in items[:limit]:
        title = item["title"]
        url = item["html_url"]
        lines.append(f"- [{title}]({url})")
    return "\n".join(lines) if lines else "_No active items_"


def replace_section(content, start, end, new_text):
    start_idx = content.index(start) + len(start)
    end_idx = content.index(end)
    return content[:start_idx] + "\n" + new_text + "\n" + content[end_idx:]


with open(README_PATH, "r", encoding="utf-8") as f:
    readme = f.read()

prs = format_items(fetch_prs())
issues = format_items(fetch_issues())

readme = replace_section(
    readme,
    "<!-- OPEN_PRS:start -->",
    "<!-- OPEN_PRS:end -->",
    prs
)

readme = replace_section(
    readme,
    "<!-- OPEN_ISSUES:start -->",
    "<!-- OPEN_ISSUES:end -->",
    issues
)

with open(README_PATH, "w", encoding="utf-8") as f:
    f.write(readme)

print("README updated successfully")
