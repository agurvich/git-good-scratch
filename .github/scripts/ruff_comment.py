"""Post (or update) one plain-words comment listing what Ruff found.

Run by .github/workflows/ruff-review.yml. Reads FILES, PR_NUMBER,
GITHUB_REPOSITORY and GH_TOKEN from the environment; talks to GitHub
with the `gh` CLI that every Actions runner has.
"""

import json
import os
import subprocess

MARKER = "<!-- ruff-review -->"
repo = os.environ["GITHUB_REPOSITORY"]
pr = os.environ["PR_NUMBER"]
files = os.environ.get("FILES", "").split()


def run(*args):
    return subprocess.run(args, capture_output=True, text=True)


findings = []
unformatted = []
if files:
    out = run("ruff", "check", "--output-format=json", *files).stdout
    findings = json.loads(out or "[]")
    fmt = run("ruff", "format", "--check", "--output-format=json", *files).stdout
    unformatted = sorted({f["filename"] for f in json.loads(fmt or "[]")})

cwd = os.getcwd() + "/"
lines = [MARKER]
total = len(findings) + len(unformatted)
if total == 0:
    lines += [
        "### Ruff found nothing to fix",
        "",
        "Ruff, the linter and formatter this project uses, checked the Python "
        "files this pull request changes and has no comments.",
    ]
else:
    noun = "problem" if total == 1 else "problems"
    lines += [
        f"### Ruff found {total} {noun} in this pull request",
        "",
        "Ruff is the linter and formatter this project uses. It checked the "
        "Python files this pull request changes.",
        "",
    ]
    if findings:
        lines.append("**Lint findings** (also pinned to the lines under *Files changed*):")
        lines.append("")
        for f in sorted(findings, key=lambda f: (f["filename"], f["location"]["row"])):
            path = f["filename"].replace(cwd, "")
            fixable = " Ruff can fix this for you." if f.get("fix") else ""
            lines.append(
                f"- `{path}`, line {f['location']['row']}: `{f['code']}`, {f['message']}.{fixable}"
            )
        lines.append("")
    if unformatted:
        lines.append("**Formatting:**")
        lines.append("")
        for path in unformatted:
            path = path.replace(cwd, "")
            lines.append(f"- `{path}` is not laid out the way `ruff format` would write it.")
        lines.append("")
    lines.append("Click **Commit suggestion** on the review comments below to apply the fixes.")
body = "\n".join(lines) + "\n"

print(body)

listing = run("gh", "api", "--paginate", f"repos/{repo}/issues/{pr}/comments")
if listing.returncode != 0:
    raise SystemExit(listing.stderr)
comments = json.loads(listing.stdout or "[]")
mine = [c for c in comments if c["user"]["login"] == "github-actions[bot]" and MARKER in c["body"]]
payload = json.dumps({"body": body})
if mine:
    endpoint, method = f"repos/{repo}/issues/comments/{mine[0]['id']}", "PATCH"
else:
    endpoint, method = f"repos/{repo}/issues/{pr}/comments", "POST"
result = subprocess.run(
    ["gh", "api", "-X", method, endpoint, "--input", "-"],
    input=payload,
    capture_output=True,
    text=True,
)
if result.returncode != 0:
    raise SystemExit(result.stderr)
