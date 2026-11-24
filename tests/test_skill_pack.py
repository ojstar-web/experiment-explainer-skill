"""Check the distributable skill pack without network or optional dependencies."""

from __future__ import annotations

import ast
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    "experiment-explainer": ROOT / "SKILL.md",
    "paper-reading-talk": ROOT / "paper-reading-talk" / "SKILL.md",
    "evidence-to-manuscript": ROOT / "evidence-to-manuscript" / "SKILL.md",
    "reader-first-dialogue": ROOT / "reader-first-dialogue" / "SKILL.md",
}


class SkillPackTests(unittest.TestCase):
    def test_each_skill_has_a_discoverable_entrypoint(self) -> None:
        for name, path in SKILLS.items():
            with self.subTest(skill=name):
                self.assertTrue(path.is_file(), path)
                body = path.read_text(encoding="utf-8-sig")
                match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", body, re.S)
                self.assertIsNotNone(match, f"Missing YAML frontmatter: {path}")
                frontmatter = match.group(1)
                self.assertRegex(frontmatter, rf"(?m)^name:\s*{re.escape(name)}\s*$")
                self.assertRegex(frontmatter, r"(?m)^description:\s*\S+")
                description = re.search(r"(?m)^description:\s*(.+)$", frontmatter).group(1)
                self.assertLessEqual(len(description), 100, f"Discovery description is too long: {path}")
                self.assertNotIn("TODO", body)

    def test_local_markdown_links_exist(self) -> None:
        for path in [ROOT / "README.md", *SKILLS.values()]:
            with self.subTest(file=path.relative_to(ROOT)):
                body = path.read_text(encoding="utf-8-sig")
                for target in re.findall(r"\]\(([^)]+)\)", body):
                    if target.startswith(("http://", "https://", "mailto:", "#")):
                        continue
                    target = target.split("#", 1)[0]
                    self.assertTrue((path.parent / target).exists(), f"Broken link in {path}: {target}")

    def test_attribution_is_visible_in_public_docs(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        dialogue = SKILLS["reader-first-dialogue"].read_text(encoding="utf-8-sig")
        for source in ("Kiterlin/anti-defensive-writing", "hardikpandya/stop-slop"):
            with self.subTest(source=source):
                self.assertIn(source, readme)
                self.assertIn(source, dialogue)

    def test_optional_python_plotter_is_valid_python(self) -> None:
        plotter = ROOT / "scripts" / "plot_series.py"
        self.assertTrue(plotter.is_file())
        ast.parse(plotter.read_text(encoding="utf-8-sig"), filename=str(plotter))
        self.assertTrue((ROOT / "scripts" / "render_markdown_pdf.cjs").is_file())

    def test_plotter_uses_named_columns(self) -> None:
        if importlib.util.find_spec("matplotlib") is None:
            self.skipTest("Optional Matplotlib dependency is not installed")
        with tempfile.TemporaryDirectory() as temp:
            data = Path(temp) / "values.csv"
            image = Path(temp) / "values.png"
            data.write_text("time,value\n0,2\n1,3\n", encoding="utf-8")
            command = [sys.executable, str(ROOT / "scripts" / "plot_series.py")]
            result = subprocess.run(
                [*command, "--csv", str(data), "--x", "time", "--y", "value", "--output", str(image)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(image.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            wrong_column = subprocess.run(
                [*command, "--csv", str(data), "--x", "time", "--y", "missing", "--output", str(image)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertNotEqual(wrong_column.returncode, 0)
            self.assertIn("Missing columns", wrong_column.stderr)

    def test_pdf_script_has_valid_javascript_syntax(self) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest("Optional Node.js runtime is not installed")
        result = subprocess.run(
            [node, "--check", str(ROOT / "scripts" / "render_markdown_pdf.cjs")],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        help_result = subprocess.run(
            [node, str(ROOT / "scripts" / "render_markdown_pdf.cjs"), "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("--preview-dir", help_result.stdout)
        self.assertIn("npm install marked playwright", help_result.stdout)

    def test_pdf_script_explains_missing_input_or_dependency(self) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest("Optional Node.js runtime is not installed")
        script = str(ROOT / "scripts" / "render_markdown_pdf.cjs")
        with tempfile.TemporaryDirectory() as temp:
            missing = subprocess.run(
                [node, script, str(Path(temp) / "absent.md")],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("Markdown source missing", missing.stderr)
            dependencies = subprocess.run(
                [node, "-e", "require.resolve('marked'); require.resolve('playwright')"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if dependencies.returncode == 0:
                return
            source = Path(temp) / "sample.md"
            source.write_text("# Test\n", encoding="utf-8")
            attempted = subprocess.run(
                [node, script, str(source)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertNotEqual(attempted.returncode, 0)
            self.assertIn("Missing dependency", attempted.stderr)
            self.assertIn("npm install marked playwright", attempted.stderr)


if __name__ == "__main__":
    unittest.main()
