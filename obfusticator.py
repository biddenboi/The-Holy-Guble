

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Final

# ----------------------------------------------------------------------------
# Match   [ any‑text ]   *unless* the bracket is part of a markdown link
# (i.e. immediately followed by '(', which we avoid via a negative look‑ahead).


# Simpler markers → anything inside a single [ … ] pair is treated as sensitive.
# One-step workflow → feed it any text/Markdown file and it spits out an obfuscated copy with a .md extension (default name: <input>_obf.md or <input>.md when the source isn’t already Markdown).
# Customisable → --placeholder lets you change the replacement text; -o/--out sets a custom output path.

#python obfusticator.py secret_notes.txt        # ➜ secret_notes.md
#python obfusticator.py report.md -o public.md
#python obfusticator.py brief.txt --placeholder OMITTED


BRACKET_CENSOR: Final[re.Pattern[str]] = re.compile(r"\[(?P<content>[^\[\]]+?)\](?!\()", re.DOTALL)


def obfuscate(source: str, placeholder: str = "REDACTED") -> str:
    """Replace every bracketed segment with a placeholder."""

    def repl(_: re.Match[str]) -> str:
        return f"[{placeholder}]"

    return BRACKET_CENSOR.sub(repl, source)


# ----------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Obfuscate bracketed text and emit a Markdown file.")
    p.add_argument("input", help="Source file to obfuscate")
    p.add_argument("-o", "--out", dest="output", help="Path for obfuscated .md file")
    p.add_argument("--placeholder", default="REDACTED",
                   help="String that replaces bracketed content (default: REDACTED)")
    return p.parse_args(argv)


def default_output_path(src: Path) -> Path:
    """Derive an output path ending in .md if the user did not specify one."""
    if src.suffix.lower() == ".md":
        return src.with_name(src.stem + "_obf.md")
    return src.with_suffix(".md")


# ----------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    ns = parse_args(argv)

    src_path = Path(ns.input)
    if not src_path.exists():
        sys.exit(f"❌  source file not found: {src_path}")

    out_path = Path(ns.output) if ns.output else default_output_path(src_path)

    source_text = src_path.read_text(encoding="utf-8")
    obfuscated = obfuscate(source_text, placeholder=ns.placeholder)

    out_path.write_text(obfuscated, encoding="utf-8")
    print(f"✅  obfuscated → {out_path}")


if __name__ == "__main__":
    main()
