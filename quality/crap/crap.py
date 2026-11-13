#!/usr/bin/env python3
"""Per-function CRAP scores from lizard complexity and test coverage. Standard library only.

CRAP = complexity^2 * (1 - coverage)^3 + complexity, per function, where complexity is
cyclomatic (lizard) and coverage is the share of the function's executable lines the tests ran.

Coverage formats, detected per file: Cobertura XML (coverlet, coverage.py `xml`), coverage.py
JSON (`coverage json`) and Istanbul JSON (`coverage-final.json` from vitest/jest). Several files
are merged: a line counts as covered if any file covered it. Coverage paths are matched to repo
files by the longest common path suffix, so absolute CI paths and Cobertura source roots work.

A function is "unmeasured" when its file lies outside every --measured prefix (no test run could
observe it). Inside a measured prefix, a file absent from all coverage data counts as 0%.

With --base, only functions whose lines changed against that commit are reported. A changed
function is "new" when no function with the same long name existed in the base version of its
file, otherwise "edited". The complexity gate (--ceiling with --block) fails when a new function
is above the ceiling, or an edited one is above the ceiling and more complex than it was.
CRAP itself never fails the run.

Exit codes: 0 ok, 1 the complexity gate failed, 2 usage or input error.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter

FIELDS = ["file", "function", "long_name", "start", "end", "nloc", "ccn", "coverage", "crap",
          "status", "change", "base_ccn", "churn90"]


# ---------------------------------------------------------------- complexity (lizard)

def parse_lizard_csv(text: str) -> list[dict]:
    rows = []
    for r in csv.reader(io.StringIO(text)):
        if len(r) < 11 or not r[1].strip().isdigit():
            continue
        nloc, ccn, _tokens, _params, _length, _location, file, func, long_name, start, end = r[:11]
        rows.append({"file": os.path.normpath(file),
                     "function": func, "long_name": long_name, "nloc": int(nloc), "ccn": int(ccn),
                     "start": int(start), "end": int(end)})
    return rows


def run_lizard(paths: list[str], cwd: str, extra: list[str]) -> list[dict]:
    out = subprocess.run(["lizard", "--csv", *extra, *paths], cwd=cwd, capture_output=True, text=True)
    if out.returncode not in (0, 1):  # lizard exits 1 when it prints warnings
        sys.stderr.write(out.stderr)
        raise SystemExit(2)
    return parse_lizard_csv(out.stdout)


# ---------------------------------------------------------------- coverage

class Coverage:
    """Executable and covered lines per coverage-reported path, before mapping to repo files."""

    def __init__(self) -> None:
        self.lines: dict[str, tuple[set[int], set[int]]] = {}  # path -> (executable, covered)

    def add(self, path: str, executable: set[int], covered: set[int]) -> None:
        exe, cov = self.lines.setdefault(path.replace("\\", "/"), (set(), set()))
        exe |= executable | covered
        cov |= covered

    def load(self, path: str) -> None:
        with open(path, "rb") as f:
            head = f.read(256).lstrip()
        if head.startswith(b"<"):
            self._cobertura(path)
            return
        with open(path) as fh:
            data = json.load(fh)
        if isinstance(data, dict) and "files" in data and "meta" in data:
            self._coverage_py(data)
        elif isinstance(data, dict):
            self._istanbul(data)
        else:
            raise ValueError(f"{path}: unknown coverage format")

    def _cobertura(self, path: str) -> None:
        root = ET.parse(path).getroot()
        sources = [s.text.strip() for s in root.iter("source") if s.text and s.text.strip()]
        for cls in root.iter("class"):
            name = cls.get("filename", "")
            full = name if os.path.isabs(name) or not sources else os.path.join(sources[0], name)
            exe, cov = set(), set()
            for line in cls.iter("line"):
                n = int(line.get("number", "0"))
                exe.add(n)
                if int(line.get("hits", "0")) > 0:
                    cov.add(n)
            self.add(full, exe, cov)

    def _coverage_py(self, data: dict) -> None:
        for name, fd in data["files"].items():
            executed = set(fd.get("executed_lines", []))
            self.add(name, executed | set(fd.get("missing_lines", [])), executed)

    def _istanbul(self, data: dict) -> None:
        for name, fd in data.items():
            if not isinstance(fd, dict) or "statementMap" not in fd:
                continue
            exe, cov = set(), set()
            for sid, loc in fd["statementMap"].items():
                line = loc["start"]["line"]
                exe.add(line)
                if fd.get("s", {}).get(sid, 0) > 0:
                    cov.add(line)
            self.add(fd.get("path", name), exe, cov)

    def by_repo_file(self, repo_files: set[str]) -> dict[str, tuple[set[int], set[int]]]:
        """Map each coverage path to the repo file with the longest common path suffix."""
        by_name: dict[str, list[str]] = {}
        for f in repo_files:
            by_name.setdefault(os.path.basename(f), []).append(f)
        mapped: dict[str, tuple[set[int], set[int]]] = {}
        for path, (exe, cov) in self.lines.items():
            parts = path.split("/")
            best, best_len = None, 0
            for cand in by_name.get(parts[-1], []):
                cparts = cand.split("/")
                n = 0
                while n < min(len(parts), len(cparts)) and parts[-1 - n] == cparts[-1 - n]:
                    n += 1
                if n > best_len:
                    best, best_len = cand, n
            if best:
                m_exe, m_cov = mapped.setdefault(best, (set(), set()))
                m_exe |= exe
                m_cov |= cov
        return mapped


# ---------------------------------------------------------------- git

def git(repo: str, *args: str) -> str:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout


def changed_lines(repo: str, base: str) -> dict[str, set[int]]:
    """New-side line numbers added or modified since the merge base of base and HEAD."""
    out = git(repo, "diff", "--unified=0", "--no-color", "--no-ext-diff", f"{base}...HEAD")
    changes: dict[str, set[int]] = {}
    current = None
    for line in out.splitlines():
        if line.startswith("+++ "):
            current = None if line.endswith("/dev/null") else line[6:] if line.startswith("+++ b/") else line[4:]
        elif line.startswith("@@") and current:
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            start, count = int(m.group(1)), int(m.group(2) or "1")
            changes.setdefault(current, set()).update(range(start, start + count))
    return changes


def base_complexity(repo: str, base: str, files: list[str], lizard_args: list[str]) -> dict[tuple[str, str], int]:
    """Complexity of each function in the base version of the given files, keyed by (file, long name)."""
    merge_base = git(repo, "merge-base", base, "HEAD").strip()
    result: dict[tuple[str, str], int] = {}
    with tempfile.TemporaryDirectory() as tmp:
        present = []
        for f in files:
            show = subprocess.run(["git", "-C", repo, "show", f"{merge_base}:{f}"], capture_output=True)
            if show.returncode != 0:
                continue  # file is new in this change
            dest = os.path.join(tmp, f)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as out:
                out.write(show.stdout)
            present.append(f)
        if present:
            for r in run_lizard(present, tmp, lizard_args):
                result[(r["file"], r["long_name"])] = max(r["ccn"], result.get((r["file"], r["long_name"]), 0))
    return result


def churn(repo: str, days: int) -> Counter:
    try:
        out = git(repo, "log", f"--since={days}.days", "--name-only", "--format=")
    except subprocess.CalledProcessError:
        return Counter()
    return Counter(line for line in out.splitlines() if line.strip())


# ---------------------------------------------------------------- scoring

def crap_score(ccn: int, coverage: float) -> float:
    return round(ccn * ccn * (1 - coverage) ** 3 + ccn, 1)


def score(functions: list[dict], cov: dict[str, tuple[set[int], set[int]]], measured: list[str]) -> None:
    for fn in functions:
        span = set(range(fn["start"], fn["end"] + 1))
        if measured and not any(fn["file"].startswith(m) for m in measured):
            fn.update(status="unmeasured", coverage=None, crap=None)
            continue
        if fn["file"] not in cov:
            fn.update(status="not-run", coverage=0.0, crap=crap_score(fn["ccn"], 0.0))
            continue
        exe, hit = cov[fn["file"]]
        exe_in, hit_in = exe & span, hit & span
        c = 1.0 if not exe_in else len(hit_in) / len(exe_in)
        fn.update(status="measured" if exe_in else "no-executable-lines", coverage=round(c, 3),
                  crap=crap_score(fn["ccn"], c))


def gate(fn: dict, ceiling: int) -> bool:
    """True when the function breaks the complexity rule (D7): new above the ceiling, or edited
    above the ceiling and more complex than before."""
    if fn["ccn"] <= ceiling:
        return False
    if fn.get("change") == "new":
        return True
    return fn.get("change") == "edited" and fn["ccn"] > (fn.get("base_ccn") or 0)


def percentile(values: list[float], p: float):
    return values[min(len(values) - 1, int(p * len(values)))] if values else None


def summary_markdown(funcs: list[dict], changed_mode: bool, ceiling: int, block: bool, failures: list[dict],
                     limit: int) -> str:
    scored = sorted(f["crap"] for f in funcs if f["crap"] is not None)
    lines = ["## CRAP scan", ""]
    if changed_mode:
        lines.append(f"{len(funcs)} changed function(s). CRAP never fails this check; "
                     f"the complexity ceiling is {ceiling} ({'blocking' if block else 'report only'}).")
    else:
        lines.append(f"{len(funcs)} function(s). Median CRAP {percentile(scored, .5)}, p90 {percentile(scored, .9)}, "
                     f"{sum(1 for s in scored if s > 30)} above 30, {sum(1 for f in funcs if f['ccn'] > ceiling)} "
                     f"above complexity {ceiling}.")
    if failures:
        lines += ["", f"**Complexity gate failed** for {len(failures)} function(s): new functions may not exceed "
                  f"{ceiling}, and edited functions above {ceiling} may not get more complex."]
    lines += ["", "CRAP = complexity² × (1 − coverage)³ + complexity. A fully tested function scores its complexity.", ""]
    if not funcs:
        lines.append("No scored functions changed.")
        return "\n".join(lines) + "\n"
    lines += ["| CRAP | Function | Complexity | Coverage | Change |", "|---:|---|---:|---:|---|"]
    order = sorted(funcs, key=lambda f: (f["crap"] is None, -(f["crap"] or 0), -f["ccn"]))
    for f in order[:limit]:
        flag = " ⛔" if f in failures else (" ⚠️" if f["ccn"] > ceiling else "")
        cov = "unmeasured" if f["coverage"] is None else f"{round(f['coverage'] * 100)}%"
        change = f.get("change") or ""
        if change == "edited" and f.get("base_ccn") is not None and f["base_ccn"] != f["ccn"]:
            change += f" ({f['base_ccn']} → {f['ccn']})"
        crap = "–" if f["crap"] is None else f"{f['crap']:,.0f}"
        lines.append(f"| {crap} | `{f['function']}`<br>`{f['file']}:{f['start']}` | {f['ccn']}{flag} | {cov} | {change} |")
    if len(order) > limit:
        lines.append(f"\n{len(order) - limit} more in the `crap-scores` artifact.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", default=".", help="repository root (default: current directory)")
    ap.add_argument("--paths", nargs="+", required=True, help="source paths for lizard, relative to --repo")
    ap.add_argument("--lizard-arg", action="append", default=[], help="extra lizard argument, repeatable (e.g. -x '*/tests/*')")
    ap.add_argument("--coverage", nargs="*", default=[], help="coverage files (Cobertura XML, coverage.py JSON, Istanbul JSON)")
    ap.add_argument("--measured", nargs="*", default=[], help="path prefixes a test run could observe; others are unmeasured")
    ap.add_argument("--exclude", nargs="*", default=[], help="regexes; matching file paths are dropped")
    ap.add_argument("--base", help="only report functions changed since this commit (merge base with HEAD)")
    ap.add_argument("--ceiling", type=int, default=10, help="complexity ceiling (default 10)")
    ap.add_argument("--block", action="store_true", help="exit 1 when the complexity gate fails")
    ap.add_argument("--churn-days", type=int, default=90)
    ap.add_argument("--out", help="write all scored functions to this CSV")
    ap.add_argument("--summary", help="append the markdown summary to this file (e.g. $GITHUB_STEP_SUMMARY)")
    ap.add_argument("--limit", type=int, default=40, help="rows in the summary table")
    a = ap.parse_args(argv)

    repo = os.path.abspath(a.repo)
    funcs = run_lizard(a.paths, repo, a.lizard_arg)
    excludes = [re.compile(x) for x in a.exclude]
    funcs = [f for f in funcs if not any(x.search(f["file"]) for x in excludes)]

    coverage = Coverage()
    for path in a.coverage:
        coverage.load(path)
    score(funcs, coverage.by_repo_file({f["file"] for f in funcs}), a.measured)
    churned = churn(repo, a.churn_days)
    for f in funcs:
        f["churn90"] = churned.get(f["file"], 0)

    failures: list[dict] = []
    if a.base:
        changes = changed_lines(repo, a.base)
        funcs = [f for f in funcs if changes.get(f["file"], set()) & set(range(f["start"], f["end"] + 1))]
        before = base_complexity(repo, a.base, sorted({f["file"] for f in funcs}), a.lizard_arg)
        for f in funcs:
            base_ccn = before.get((f["file"], f["long_name"]))
            f["change"] = "new" if base_ccn is None else "edited"
            f["base_ccn"] = base_ccn
        failures = [f for f in funcs if gate(f, a.ceiling)]

    if a.out:
        with open(a.out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
            w.writeheader()
            w.writerows(funcs)
    text = summary_markdown(funcs, bool(a.base), a.ceiling, a.block, failures, a.limit)
    if a.summary:
        with open(a.summary, "a") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
    return 1 if (a.block and failures) else 0


if __name__ == "__main__":
    sys.exit(main())
