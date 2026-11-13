# CRAP scan

Shows, on every pull request, how risky the changed functions are: complex code with weak tests.

CRAP = complexity² × (1 − coverage)³ + complexity, per function. A fully tested function scores its cyclomatic complexity. An untested one scores complexity² + complexity, so a complexity-10 function goes from 10 to 110.

## What runs where

| Part | Lives in | Does |
|---|---|---|
| Tests with coverage | the calling repo's own test job | Runs the repo's tests with coverage on, then uploads the coverage files as an artifact. Each repo keeps its own test setup (databases, migrations, services). |
| `crap.yml` (reusable workflow) | this repo, `.github/workflows/crap.yml` | Checks out the caller, runs lizard on the source paths, joins the result with the coverage files, and writes the table to the job summary. It also uploads `crap-scores.csv`. |
| `crap.py` | this repo, `quality/crap/` | The scoring. Standard library only, with tests in `test_crap.py`. |

On a pull request the summary lists the functions the PR changed, marked `new` or `edited` (with the complexity before and after). On a push or schedule it summarises the whole repository.

## The rules (Orbit decisions D1, D7)

- CRAP never fails the job. It is information for the reviewer and the merge record.
- The complexity gate fails the job only when the caller sets `block: true`:
  - a new function above the ceiling (default 10) fails;
  - an edited function above the ceiling fails only if it got more complex (the ratchet), so legacy code is never blocked for being touched.
- A repo with legacy code runs report-only (`block: false`) for two waves, then turns blocking on.
- In .NET repos the build already enforces the ceiling (CA1502 at 10), so they call with `block: false`.

## Coverage formats

Detected per file: Cobertura XML (coverlet, `coverage xml`), coverage.py JSON (`coverage json`) and Istanbul JSON (`coverage-final.json` from vitest or jest). Several files are merged: a line counts as covered if any test run covered it. Paths are matched to repository files by their longest common path suffix, so CI paths and Cobertura source roots need no configuration.

Functions under the `measured` prefixes but absent from every coverage file count as 0%. Functions outside them are reported as `unmeasured`, never as 0%. Use this for code no test run can observe, such as scripts or code that only runs in another environment.

## Calling it

```yaml
jobs:
  build-test:
    # ... the repo's own test job, ending with:
    steps:
      - run: <tests with coverage on>
      - uses: actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2
        with:
          name: coverage
          path: "**/coverage*.xml"

  crap:
    needs: build-test
    uses: mschabow/agentic-sdlc/.github/workflows/crap.yml@<commit sha>
    with:
      tools-ref: <same commit sha>
      paths: src
      coverage-artifact: coverage
      measured: src/
      lizard-exclude: |
        */tests/*
        */Migrations/*
      block: false
```

Pin both `uses:` and `tools-ref` to the same commit.

## Tools

`requirements.txt` pins lizard and its two dependencies by version and hash. Each passed the 7-day age rule and an OSV.dev check. They are installed with `--require-hashes` in the workflow and never enter the calling repo's lockfile. A change goes through a reviewed PR here, so every caller picks it up only when it moves its pin.

## Running it locally

```bash
python -m pip install --require-hashes --no-deps -r quality/crap/requirements.txt
python quality/crap/crap.py --repo <repo> --paths src --coverage <files> --measured src/ --base origin/main
```

Leave out `--base` for a whole-repository report, and add `--out scores.csv` for every function.
