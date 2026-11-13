"""Tests for crap.py. Run: python3 -m unittest discover -s quality/crap"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import crap  # noqa: E402

HAS_LIZARD = shutil.which("lizard") is not None


class Formula(unittest.TestCase):
    def test_fully_covered_scores_its_complexity(self):
        self.assertEqual(crap.crap_score(6, 1.0), 6.0)

    def test_uncovered_scores_complexity_squared_plus_complexity(self):
        self.assertEqual(crap.crap_score(6, 0.0), 42.0)

    def test_half_covered(self):
        self.assertEqual(crap.crap_score(10, 0.5), 22.5)


class LizardCsv(unittest.TestCase):
    def test_parses_rows_and_skips_headers(self):
        text = ('NLOC,CCN,token,PARAM,length,location,file,function,long_name,start,end\n'
                '12,4,80,1,14,"f@3-16@./src/a.py","./src/a.py","f","f( x )",3,16\n')
        rows = crap.parse_lizard_csv(text)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["file"], "src/a.py")
        self.assertEqual((rows[0]["ccn"], rows[0]["start"], rows[0]["end"]), (4, 3, 16))


class CoverageFormats(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, name, text):
        path = os.path.join(self.tmp, name)
        with open(path, "w") as f:
            f.write(text)
        return path

    def test_cobertura_with_source_root(self):
        path = self.write("c.xml", textwrap.dedent("""\
            <?xml version="1.0"?>
            <coverage><sources><source>/home/runner/work/app/app/src/</source></sources>
            <packages><package><classes>
              <class filename="Modules/People/Directory.cs"><lines>
                <line number="10" hits="3"/><line number="11" hits="0"/>
              </lines></class>
            </classes></package></packages></coverage>"""))
        cov = crap.Coverage()
        cov.load(path)
        mapped = cov.by_repo_file({"src/Modules/People/Directory.cs", "src/Other/Directory.cs"})
        self.assertEqual(mapped["src/Modules/People/Directory.cs"], ({10, 11}, {10}))
        self.assertNotIn("src/Other/Directory.cs", mapped)

    def test_coverage_py_json(self):
        path = self.write("c.json", json.dumps({"meta": {}, "files": {"app/x.py": {
            "executed_lines": [1, 2], "missing_lines": [3]}}}))
        cov = crap.Coverage()
        cov.load(path)
        self.assertEqual(cov.by_repo_file({"server/app/x.py"})["server/app/x.py"], ({1, 2, 3}, {1, 2}))

    def test_istanbul_json(self):
        path = self.write("i.json", json.dumps({"/abs/web/src/a.ts": {
            "path": "/abs/web/src/a.ts",
            "statementMap": {"0": {"start": {"line": 4}}, "1": {"start": {"line": 5}}},
            "s": {"0": 2, "1": 0}}}))
        cov = crap.Coverage()
        cov.load(path)
        self.assertEqual(cov.by_repo_file({"web/src/a.ts"})["web/src/a.ts"], ({4, 5}, {4}))

    def test_files_merge_covered_if_any_run_covered(self):
        a = self.write("a.json", json.dumps({"meta": {}, "files": {"x.py": {"executed_lines": [1], "missing_lines": [2]}}}))
        b = self.write("b.json", json.dumps({"meta": {}, "files": {"x.py": {"executed_lines": [2], "missing_lines": [1]}}}))
        cov = crap.Coverage()
        cov.load(a)
        cov.load(b)
        self.assertEqual(cov.by_repo_file({"x.py"})["x.py"], ({1, 2}, {1, 2}))


class Scoring(unittest.TestCase):
    def fn(self, **kw):
        base = {"file": "src/a.py", "function": "f", "long_name": "f()", "start": 1, "end": 4, "nloc": 4, "ccn": 4}
        base.update(kw)
        return base

    def test_measured_partial(self):
        f = self.fn()
        crap.score([f], {"src/a.py": ({1, 2, 3, 4}, {1, 2})}, ["src/"])
        self.assertEqual((f["status"], f["coverage"], f["crap"]), ("measured", 0.5, 6.0))

    def test_outside_measured_prefix_is_unmeasured_not_zero(self):
        f = self.fn(file="tools/b.py")
        crap.score([f], {}, ["src/"])
        self.assertEqual((f["status"], f["coverage"], f["crap"]), ("unmeasured", None, None))

    def test_measured_file_missing_from_coverage_counts_as_zero(self):
        f = self.fn()
        crap.score([f], {}, ["src/"])
        self.assertEqual((f["status"], f["crap"]), ("not-run", 20.0))


class Gate(unittest.TestCase):
    def test_new_function_above_ceiling_fails(self):
        self.assertTrue(crap.gate({"ccn": 11, "change": "new"}, 10))

    def test_new_function_at_ceiling_passes(self):
        self.assertFalse(crap.gate({"ccn": 10, "change": "new"}, 10))

    def test_edited_function_that_got_more_complex_fails(self):
        self.assertTrue(crap.gate({"ccn": 14, "change": "edited", "base_ccn": 12}, 10))

    def test_edited_legacy_function_not_made_worse_passes(self):
        self.assertFalse(crap.gate({"ccn": 14, "change": "edited", "base_ccn": 14}, 10))


@unittest.skipUnless(HAS_LIZARD, "lizard not installed")
class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.git("config", "commit.gpgsign", "false")
        os.makedirs(os.path.join(self.repo, "src"))
        self.write("src/a.py", "def old(x):\n    if x:\n        return 1\n    return 0\n")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.base = self.git("rev-parse", "HEAD").strip()

    def tearDown(self):
        shutil.rmtree(self.repo)

    def git(self, *args):
        return subprocess.run(["git", "-C", self.repo, *args], capture_output=True, text=True, check=True).stdout

    def write(self, rel, text):
        with open(os.path.join(self.repo, rel), "w") as f:
            f.write(text)

    def branchy(self, name, n):
        body = "".join(f"    if x == {i}:\n        return {i}\n" for i in range(n - 1))
        return f"def {name}(x):\n{body}    return -1\n"

    def test_new_complex_function_fails_only_with_block(self):
        self.write("src/a.py", "def old(x):\n    if x:\n        return 1\n    return 0\n\n\n" + self.branchy("big", 12))
        self.git("commit", "-qam", "add big")
        summary = os.path.join(self.repo, "summary.md")
        args = ["--repo", self.repo, "--paths", "src", "--base", self.base, "--summary", summary]
        self.assertEqual(crap.main(args), 0)
        self.assertEqual(crap.main(args + ["--block"]), 1)
        with open(summary) as fh:
            text = fh.read()
        self.assertIn("`big`", text)
        self.assertNotIn("`old`", text)
        self.assertIn("Complexity gate failed", text)

    def test_unchanged_repo_reports_nothing_changed(self):
        summary = os.path.join(self.repo, "summary.md")
        self.assertEqual(crap.main(["--repo", self.repo, "--paths", "src", "--base", self.base,
                                    "--summary", summary, "--block"]), 0)
        with open(summary) as fh:
            self.assertIn("No scored functions changed.", fh.read())


if __name__ == "__main__":
    unittest.main()
