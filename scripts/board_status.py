#!/usr/bin/env python3
"""Move an article's card on the project board to match the stages checked off on its issue.

Run by .github/workflows/board.yml whenever an article issue is edited (checking a box edits
the issue). It reads the event GitHub sends, finds the furthest stage checked off in the
issue's Stages checklist, and sets the card's Status to the column that comes next. Unchecking
a box moves the card back.

Needs the gh CLI, signed in with a token that can edit the organization's board
(GH_TOKEN). Settings come from the environment:

    PROJECT_OWNER   the organization that owns the board, e.g. ncssm
    PROJECT_NUMBER  the board's number, e.g. 1
    EVENT_PATH      the event payload (defaults to GITHUB_EVENT_PATH)

    python3 scripts/board_status.py --dry-run    # print the move without making it
"""

import json
import os
import re
import subprocess
import sys

# The furthest stage checked off decides the card's column: the column for the work that
# comes next. Stages are the checkbox labels in .github/ISSUE_TEMPLATE/new-article.yml.
STAGE_TO_COLUMN = [
    ("Handed off", "Conversion"),
    ("Conversion", "Conversion"),
    ("Checks", "Author proof"),
    ("Author proof", "Copy edit"),
    ("Copy edit", "Copy edit"),
    ("Merged", "Submitted"),
]
NOTHING_CHECKED = "Intake"
TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}


def graphql(query, **variables):
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for name, value in variables.items():
        args += ["-F" if isinstance(value, int) else "-f", f"{name}={value}"]
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode:
        sys.exit(f"GitHub API error: {out.stderr.strip()}")
    return json.loads(out.stdout)["data"]


def column_for(body: str) -> str:
    """The column for an issue description, from its Stages checklist."""
    section = re.split(r"^###\s+Stages\s*$", body or "", flags=re.M)
    if len(section) < 2:
        return NOTHING_CHECKED
    stages = re.split(r"^###\s", section[1], flags=re.M)[0]
    checked = {m.group(1).strip() for m in re.finditer(r"^- \[[xX]\]\s+([^:\n]+):", stages, re.M)}
    column = NOTHING_CHECKED
    for stage, target in STAGE_TO_COLUMN:
        if stage in checked:
            column = target
    return column


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    event = json.load(open(os.environ.get("EVENT_PATH") or os.environ["GITHUB_EVENT_PATH"]))
    issue = event["issue"]
    labels = {label["name"] for label in issue.get("labels", [])}

    if "article" not in labels:
        print(f"#{issue['number']} isn't an article issue; nothing to do.")
        return 0
    if issue.get("author_association") not in TRUSTED:
        print(f"#{issue['number']} was opened by someone outside the repo; leaving its card alone.")
        return 0
    if issue.get("state") == "closed":
        print(f"#{issue['number']} is closed; the board's own rule handles closed issues.")
        return 0

    column = column_for(issue.get("body", ""))
    owner, number = os.environ["PROJECT_OWNER"], int(os.environ["PROJECT_NUMBER"])

    board = graphql("""
      query($owner: String!, $number: Int!) {
        organization(login: $owner) { projectV2(number: $number) {
          id
          field(name: "Status") { ... on ProjectV2SingleSelectField { id options { id name } } }
        } }
      }""", owner=owner, number=number)["organization"]["projectV2"]
    options = {o["name"]: o["id"] for o in board["field"]["options"]}
    if column not in options:
        sys.exit(f"The board has no '{column}' column. Columns: {', '.join(options)}")

    items = graphql("""
      query($id: ID!) {
        node(id: $id) { ... on Issue { projectItems(first: 20) { nodes {
          id fieldValueByName(name: "Status") { ... on ProjectV2ItemFieldSingleSelectValue { name } }
          project { id }
        } } } }
      }""", id=issue["node_id"])["node"]["projectItems"]["nodes"]
    item = next((i for i in items if i["project"]["id"] == board["id"]), None)
    current = (item or {}).get("fieldValueByName") or {}

    if current.get("name") == column:
        print(f"#{issue['number']} is already in {column}.")
        return 0
    print(f"#{issue['number']}: {current.get('name', 'not on the board')} -> {column}")
    if dry_run:
        return 0

    if item is None:
        item = graphql("""
          mutation($project: ID!, $content: ID!) {
            addProjectV2ItemById(input: {projectId: $project, contentId: $content}) { item { id } }
          }""", project=board["id"], content=issue["node_id"])["addProjectV2ItemById"]["item"]
    graphql("""
      mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
        updateProjectV2ItemFieldValue(input: {projectId: $project, itemId: $item, fieldId: $field,
          value: {singleSelectOptionId: $option}}) { projectV2Item { id } }
      }""", project=board["id"], item=item["id"], field=board["field"]["id"], option=options[column])
    return 0


if __name__ == "__main__":
    sys.exit(main())
