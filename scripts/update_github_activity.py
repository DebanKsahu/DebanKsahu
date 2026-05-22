import os
import requests

TOKEN = os.getenv("GH_TOKEN")

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


def fetch_data():
    url = "https://api.github.com/graphql"
    res = requests.post(url, json={"query": QUERY}, headers=HEADERS)

    if res.status_code != 200:
        raise Exception(f"GitHub API error: {res.text}")

    return res.json()["data"]["viewer"]


def build_markdown(data):
    prs = data["pullRequests"]["nodes"]
    issues = data["issues"]["nodes"]

    def pr_line(pr):
        icon = "🟢" if pr["state"] == "OPEN" else "🔵"
        repo = pr["repository"]["name"]
        return f"- {icon} **{pr['title']}** (`{repo}`) → {pr['url']}"

    def issue_line(issue):
        icon = "🟢" if issue["state"] == "OPEN" else "🔴"
        repo = issue["repository"]["name"]
        return f"- {icon} **{issue['title']}** (`{repo}`) → {issue['url']}"

    pr_section = "\n".join(pr_line(p) for p in prs) or "_No recent PRs_"
    issue_section = "\n".join(issue_line(i) for i in issues) or "_No recent issues_"

    return f"""
## 🚀 Latest GitHub Activity

### 🟣 Pull Requests (Latest 10)
{pr_section}

---

### 🐞 Issues (Latest 10)
{issue_section}
""".strip()


def update_readme(content):
    with open("README.md", "r", encoding="utf-8") as f:
        old = f.read()

    start = "<!--START_GH_ACTIVITY-->"
    end = "<!--END_GH_ACTIVITY-->"

    if start not in old or end not in old:
        raise Exception("Missing README markers")

    before = old.split(start)[0]
    after = old.split(end)[1]

    new_block = f"{start}\n{content}\n{end}"

    updated = before + new_block + after

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)


if __name__ == "__main__":
    data = fetch_data()
    markdown = build_markdown(data)
    update_readme(markdown)