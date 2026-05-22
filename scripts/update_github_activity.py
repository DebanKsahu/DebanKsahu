import os
import requests

TOKEN = os.getenv("GH_TOKEN")

if not TOKEN:
    raise Exception("GH_TOKEN is missing in environment variables")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

QUERY = """
query {
  viewer {
    pullRequests(first: 10, orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        title
        url
        state
        repository {
          name
        }
      }
    }
    issues(first: 10, orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        title
        url
        state
        repository {
          name
        }
      }
    }
  }
}
"""


# ---------------- FETCH DATA ---------------- #

def fetch_data():
    url = "https://api.github.com/graphql"

    res = requests.post(
        url,
        json={"query": QUERY},
        headers=HEADERS
    )

    if res.status_code != 200:
        raise Exception(f"GitHub API error {res.status_code}: {res.text}")

    data = res.json()

    if "errors" in data:
        raise Exception(f"GraphQL error: {data['errors']}")

    return data["data"]["viewer"]


# ---------------- FORMAT PR ---------------- #

def pr_line(pr):
    if not pr:
        return ""

    repo = pr.get("repository", {}).get("name", "unknown")
    state = pr.get("state", "UNKNOWN")

    icon = "🟢" if state == "OPEN" else "🔵"
    title = pr.get("title", "No title")
    url = pr.get("url", "#")

    return f"- {icon} **{title}** (`{repo}`) → {url}"


# ---------------- FORMAT ISSUE ---------------- #

def issue_line(issue):
    if not issue:
        return ""

    repo = issue.get("repository", {}).get("name", "unknown")
    state = issue.get("state", "UNKNOWN")

    icon = "🟢" if state == "OPEN" else "🔴"
    title = issue.get("title", "No title")
    url = issue.get("url", "#")

    return f"- {icon} **{title}** (`{repo}`) → {url}"


# ---------------- BUILD MARKDOWN ---------------- #

def build_markdown(data):
    prs = data.get("pullRequests", {}).get("nodes", []) or []
    issues = data.get("issues", {}).get("nodes", []) or []

    prs = [p for p in prs if p]
    issues = [i for i in issues if i]

    def format_pr(p):
        repo = p.get("repository", {}).get("name", "unknown")
        title = p.get("title", "No title")
        url = p.get("url", "#")
        state = p.get("state", "UNKNOWN")

        icon = "🟢" if state == "OPEN" else "🔵"

        return f"""
**{icon} {title}**
`{repo}`
→ [view PR]({url})
""".strip()

    def format_issue(i):
        repo = i.get("repository", {}).get("name", "unknown")
        title = i.get("title", "No title")
        url = i.get("url", "#")
        state = i.get("state", "UNKNOWN")

        icon = "🟢" if state == "OPEN" else "🔴"

        return f"""
**{icon} {title}**
`{repo}`
→ [view issue]({url})
""".strip()

    pr_block = "\n\n---\n\n".join(format_pr(p) for p in prs) or "_No recent PRs_"
    issue_block = "\n\n---\n\n".join(format_issue(i) for i in issues) or "_No recent issues_"

    return f"""
### 🚀 Pull Requests (Latest 10)

{pr_block}

---

### 🐞 Issues (Latest 10)

{issue_block}
""".strip()


# ---------------- UPDATE README ---------------- #

def update_readme(content):
    start_marker = "<!--START_GH_ACTIVITY-->"
    end_marker = "<!--END_GH_ACTIVITY-->"

    with open("README.md", "r", encoding="utf-8") as f:
        text = f.read()

    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        raise Exception("Missing GH activity markers")

    start_idx += len(start_marker)

    # Preserve everything outside the block EXACTLY
    before = text[:start_idx]
    after = text[end_idx:]

    new_text = before + "\n\n" + content.strip() + "\n\n" + after

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_text)


# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    data = fetch_data()
    markdown = build_markdown(data)
    update_readme(markdown)

    print("✅ GitHub activity updated successfully")