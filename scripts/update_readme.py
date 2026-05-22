import os
import requests

USERNAME = "DebanKsahu"
README_PATH = "README.md"

TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
} if TOKEN else {}


def safe_get(url):
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"GitHub API error: {res.status_code} -> {res.text}")
    return res.json()


def fetch_prs():
    url = f"https://api.github.com/search/issues?q=author:{USERNAME}+type:pr+state:open&sort=updated&order=desc"
    return safe_get(url).get("items", [])


def fetch_issues():
    url = f"https://api.github.com/search/issues?q=author:{USERNAME}+type:issue+state:open&sort=updated&order=desc"
    return safe_get(url).get("items", [])


def format_items(items):
    if not items:
        return "_No active items_"

    return "\n".join(
        f"- [{item['title']}]({item['html_url']})"
        for item in items[:10]
    )


def replace_block(content, start, end, new_text):
    before = content.split(start)[0]
    after = content.split(end)[1]
    return before + start + "\n" + new_text + "\n" + end + after


with open(README_PATH, "r", encoding="utf-8") as f:
    readme = f.read()

prs = format_items(fetch_prs())
issues = format_items(fetch_issues())

readme = replace_block(
    readme,
    "<!-- OPEN_PRS:start -->",
    "<!-- OPEN_PRS:end -->",
    prs
)

readme = replace_block(
    readme,
    "<!-- OPEN_ISSUES:start -->",
    "<!-- OPEN_ISSUES:end -->",
    issues
)

with open(README_PATH, "w", encoding="utf-8") as f:
    f.write(readme)

print("README updated successfully")
