#!/usr/bin/env python3
"""Rewrite the install path for the cailum-blue/agentic-sdlc mirror.

The mirror workflow (.github/workflows/mirror-to-cailum-blue.yml) runs this on a checkout of
mschabow/agentic-sdlc, commits the result on top and force-pushes it to cailum-blue/agentic-sdlc.
Teammates keep installing from cailum-blue under the marketplace name sw-development-process.

Fails if a required pattern is missing, so a README or marketplace change cannot silently
break the work repo's install instructions.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

MIRROR_NOTE = (
    "This copy at `cailum-blue/agentic-sdlc` is internal and is mirrored automatically from "
    "[`mschabow/agentic-sdlc`](https://github.com/mschabow/agentic-sdlc): teammates need read access "
    "to the `cailum-blue` org, or `/plugin marketplace add` fails with an auth error. Make changes in "
    "`mschabow/agentic-sdlc`; anything pushed here directly is overwritten by the next mirror."
)

# (file, old, new, required)
REPLACEMENTS = [
    ("README.md", "marketplace add mschabow/agentic-sdlc", "marketplace add cailum-blue/agentic-sdlc", True),
    ("README.md", "sdlc-workflow@agentic-sdlc", "sdlc-workflow@sw-development-process", True),
    ("rollout.md", "marketplace add mschabow/agentic-sdlc", "marketplace add cailum-blue/agentic-sdlc", True),
    ("rollout.md", "sdlc-workflow@agentic-sdlc", "sdlc-workflow@sw-development-process", True),
    (
        "rollout.md",
        "The repo lives at `github.com/mschabow/agentic-sdlc` (public).",
        "The canonical repo is `github.com/mschabow/agentic-sdlc` (public); `cailum-blue/agentic-sdlc` "
        "is an internal mirror that teammates install from.",
        False,
    ),
]


def main() -> int:
    errors = []

    marketplace = ROOT / ".claude-plugin" / "marketplace.json"
    data = json.loads(marketplace.read_text())
    data["name"] = "sw-development-process"
    marketplace.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    for name, old, new, required in REPLACEMENTS:
        path = ROOT / name
        text = path.read_text()
        if old not in text:
            (errors if required else []).append(f"{name}: {old!r} not found")
            continue
        path.write_text(text.replace(old, new))

    readme = ROOT / "README.md"
    lines = readme.read_text().splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if line.startswith("This repo is public")]
    if hits:
        lines[hits[0]] = MIRROR_NOTE + "\n"
        readme.write_text("".join(lines))
    else:
        errors.append("README.md: 'This repo is public' paragraph not found")

    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
