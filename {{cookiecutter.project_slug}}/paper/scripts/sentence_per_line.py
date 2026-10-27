#!/usr/bin/env python3
"""Reformat LaTeX prose so each sentence sits on its own line.

Newlines are spaces to LaTeX, so this changes only the source layout (for
cleaner git diffs), never the typeset output. Structure is preserved:

- everything before \\begin{document} passes through untouched
- equation/align/tabular/verbatim environments pass through untouched
- comment lines, blank lines, and structural one-liners (\\section, \\label,
  \\includegraphics, ...) pass through untouched
- multi-line \\caption{...} arguments are joined, then split by sentence
- prose paragraphs are joined, then split after sentence-ending punctuation,
  with common abbreviations (et al., e.g., St., ...) protected

Usage: python3 scripts/sentence_per_line.py main.tex [more.tex ...]
Rewrites each file in place.
"""

import re
import sys

# Periods in these never end a sentence.
ABBREVS = [
    r"et al\.", r"e\.g\.", r"i\.e\.", r"vs\.", r"cf\.", r"etc\.",
    r"St\.", r"Fig\.", r"Figs\.", r"Eq\.", r"Eqs\.", r"Sec\.", r"Secs\.",
    r"Tab\.", r"No\.", r"Dr\.", r"Mr\.", r"Ms\.", r"Prof\.", r"approx\.",
]
ABBREV_RE = re.compile("|".join(ABBREVS))
PLACEHOLDER = "\x00"

# Environments whose bodies are never reflowed.
PASSTHROUGH_ENVS = {
    "equation", "equation*", "align", "align*", "tabular", "verbatim",
    "lstlisting", "array",
}

# Lines that stand alone even inside a prose paragraph.
STRUCTURAL_RE = re.compile(
    r"^\\("
    r"begin|end|label|input|include|includegraphics|centering|maketitle|"
    r"section|subsection|subsubsection|appendix|printbibliography|"
    r"clearpage|newpage|addbibresource|title|author|affiliation|email|"
    r"usepackage|documentclass|newcommand|renewcommand|colorlet|"
    r"makeatletter|makeatother|patchcmd|pretocmd|setlength|small|"
    r"scriptsize|footnotesize|toprule|midrule|bottomrule|multicolumn|"
    r"iffalse\b|fi\b|item\b"
    r")",
)


def split_sentences(text):
    """Return text with one sentence per line."""
    text = re.sub(r"\s+", " ", text.strip())
    protected = ABBREV_RE.sub(lambda m: m.group().replace(".", PLACEHOLDER), text)
    protected = re.sub(
        r"([.!?][\'\")\}\]]*) (?=[A-Za-z\\])", r"\1\n", protected
    )
    return protected.replace(PLACEHOLDER, ".")


def brace_delta(line):
    """Net change in brace depth, ignoring escaped braces and comments."""
    line = re.sub(r"\\%", "", line)
    line = re.sub(r"(?<!\\)%.*", "", line)
    line = re.sub(r"\\[{}]", "", line)
    return line.count("{") - line.count("}")


def reformat(lines):
    out = []
    buf = []  # current prose paragraph, as raw lines
    env_stack = []  # pass-through environments we are inside
    in_document = False
    i = 0

    def flush():
        if buf:
            out.append(split_sentences(" ".join(buf)))
            buf.clear()

    while i < len(lines):
        line = lines[i].rstrip("\n")
        stripped = line.strip()

        if not in_document:
            out.append(line)
            if stripped.startswith(r"\begin{document}"):
                in_document = True
            i += 1
            continue

        begin = re.match(r"\\begin\{([^}]+)\}", stripped)
        end = re.match(r"\\end\{([^}]+)\}", stripped)

        if env_stack:
            out.append(line)
            if begin and begin.group(1) in PASSTHROUGH_ENVS:
                env_stack.append(begin.group(1))
            elif end and end.group(1) == env_stack[-1]:
                env_stack.pop()
            i += 1
            continue

        if begin and begin.group(1) in PASSTHROUGH_ENVS:
            flush()
            out.append(line)
            env_stack.append(begin.group(1))
            i += 1
            continue

        if not stripped or stripped.startswith("%"):
            flush()
            out.append(line)
            i += 1
            continue

        if stripped.startswith(r"\caption{"):
            flush()
            caption = [line]
            depth = brace_delta(line)
            while depth > 0 and i + 1 < len(lines):
                i += 1
                nxt = lines[i].rstrip("\n")
                caption.append(nxt)
                depth += brace_delta(nxt)
            out.append(split_sentences(" ".join(caption)))
            i += 1
            continue

        if STRUCTURAL_RE.match(stripped):
            flush()
            out.append(line)
            i += 1
            continue

        buf.append(stripped)
        i += 1

    flush()
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__.strip())
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        result = reformat(lines)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(result) + "\n")
        print(f"{path}: reformatted")


if __name__ == "__main__":
    main()
