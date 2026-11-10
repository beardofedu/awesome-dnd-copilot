#!/usr/bin/env python3
"""Build the static resource catalog from the library's current Markdown."""

import argparse
import html
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
PHASES = {
    "campaign-creation": "Campaign creation",
    "campaign-maintenance": "Campaign maintenance",
    "running-campaign": "Running a campaign",
}
ALL_PHASES = list(PHASES.values())

# Audience is an editorial classification, not a permission or safety guarantee.
AUDIENCES = {
    "campaign-creation/agents/session-zero.md": ["Shared table"],
    "campaign-creation/session-kits/session-zero/README.md": ["Shared table"],
    "campaign-maintenance/session-kits/party-journal/README.md": ["Players"],
    "campaign-maintenance/session-kits/player-submissions/README.md": [
        "DM", "Players"
    ],
    "campaign-maintenance/session-kits/player-safe-release/README.md": [
        "DM", "Players"
    ],
}
EXTRAS = [
    ("campaign-creation/templates/campaign-starter/README.md",
     ["Campaign creation"], ["DM"], ["Workspace template"], ["No Copilot required"]),
    ("campaign-creation/templates/player-starter/README.md",
     ["Campaign creation"], ["Players"], ["Workspace template"],
     ["Repository instructions"]),
    ("campaign-creation/templates/campaign-player-site/README.md",
     ["Campaign creation"], ["Players"], ["Static site scaffold", "Manual prompt"],
     ["Chat prompts", "No Copilot required"]),
    ("tools/campaign-starter/README.md", ALL_PHASES, ["DM", "Players"],
     ["Local Python"], ["No Copilot required"]),
    ("campaign-maintenance/actions/session-note-importers/README.md",
     ["Campaign maintenance"], ["DM"], ["Optional Actions workflow"],
     ["No Copilot required"]),
    ("examples/first-campaign/README.md", ALL_PHASES, ["DM", "Players"],
     ["Read-through guide"], ["Repository instructions", "Custom agents", "Chat prompts"]),
]


def plain(text):
    """Reduce the inline Markdown used in source introductions to plain text."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"[*`]", "", text).strip()


def source_text(path):
    text = (ROOT / path).read_text(encoding="utf-8")
    title = re.search(r"^# (.+)$", text, re.MULTILINE)
    if not title:
        raise ValueError(f"{path}: missing resource title")
    if "/agents/" in path:
        description = re.search(r"^description: (.+)$", text, re.MULTILINE)
        if not description:
            raise ValueError(f"{path}: missing agent description")
        summary = description.group(1)
    else:
        summary = text[title.end():].strip().split("\n\n", 1)[0]
    return plain(title.group(1)), plain(" ".join(summary.split()))


def resource(path, phases, audiences, setups, features):
    title, summary = source_text(path)
    return dict(path=path, title=title, summary=summary, phase=phases,
                audience=audiences, setup=setups, feature=features)


def resources():
    entries = []
    for folder, phase in PHASES.items():
        entries.append(resource(f"{folder}/copilot-instructions.md", [phase],
                                ["DM"], ["Copy-in instructions"],
                                ["Repository instructions"]))
        for path in sorted((ROOT / folder / "agents").glob("*.md")):
            relative = path.relative_to(ROOT).as_posix()
            entries.append(resource(relative, [phase],
                                    AUDIENCES.get(relative, ["DM"]),
                                    ["Copy-in agent"], ["Custom agents"]))
        for readme in sorted((ROOT / folder / "session-kits").glob("*/README.md")):
            kit = readme.parent
            relative = readme.relative_to(ROOT).as_posix()
            setups, features = ["Manual prompt"], ["Chat prompts"]
            if (kit / "canvas.prompt.md").is_file():
                setups.append("Canvas generation")
                features.append("Canvas")
            if list(kit.glob("*.recipe.json")):
                setups.append("Optional cloud automation")
                features.append("Cloud automations")
            if list(kit.glob("*.py")):
                setups.append("Local Python")
                features.append("No Copilot required")
            if list(kit.glob("*workflow*.yml*")):
                setups.append("Optional Actions workflow")
            if (kit / "submission-form.yml").is_file():
                setups.append("Issue form")
            entries.append(resource(relative, [phase],
                                    AUDIENCES.get(relative, ["DM"]),
                                    setups, features))
    entries.extend(resource(*entry) for entry in EXTRAS)
    return sorted(entries, key=lambda entry: (entry["phase"][0], entry["title"]))


def render():
    entries = resources()
    controls = []
    for key, label in [("phase", "Campaign phase"), ("audience", "Audience"),
                       ("setup", "Setup type"), ("feature", "Copilot feature")]:
        values = sorted({value for entry in entries for value in entry[key]})
        options = "".join(f'<option>{html.escape(value)}</option>' for value in values)
        controls.append(
            f'<label for="{key}">{label}<select id="{key}" name="{key}">'
            f'<option value="">All</option>{options}</select></label>'
        )
    cards = []
    for entry in entries:
        attributes = " ".join(
            f'data-{key}="{html.escape("|".join(entry[key]), quote=True)}"'
            for key in ("phase", "audience", "setup", "feature")
        )
        details = "".join(
            f"<div><dt>{label}</dt><dd>{html.escape(', '.join(entry[key]))}</dd></div>"
            for key, label in [("phase", "Phase"), ("audience", "Audience"),
                               ("setup", "Setup"), ("feature", "Copilot")]
        )
        path = html.escape(entry["path"], quote=True)
        cards.append(
            f'<li class="resource" {attributes}>\n'
            f'  <article><h3><a href="https://github.com/beardofedu/awesome-dnd-copilot/'
            f'blob/main/{path}">{html.escape(entry["title"])}</a></h3>\n'
            f'  <p>{html.escape(entry["summary"])}</p>\n'
            f'  <dl>{details}</dl>\n'
            f'  <p class="source">{path}</p></article>\n</li>'
        )
    template = (HERE / "page.html").read_text(encoding="utf-8")
    return (template.replace("{{filters}}", "\n".join(controls))
            .replace("{{cards}}", "\n".join(cards))
            .replace("{{count}}", str(len(entries))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="fail if the committed catalog needs regeneration")
    args = parser.parse_args()
    output = render()
    destination = HERE / "index.html"
    if args.check:
        if not destination.is_file() or destination.read_text(encoding="utf-8") != output:
            parser.exit(1, "Catalog is stale. Run python3 catalog/build.py\n")
        print("Catalog matches current source resources.")
    else:
        destination.write_text(output, encoding="utf-8")
        print(f"Built {len(resources())} resources in catalog/index.html")


if __name__ == "__main__":
    main()
