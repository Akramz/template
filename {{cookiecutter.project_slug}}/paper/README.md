# Paper

`main.tex` is the manuscript. It uses `cup-journal.cls`, the lab's LaTeX class, set to the
technical-report layout. Build it with:

```console
make
```

`make` runs `latexmk` and writes `main.pdf`. Other targets:

| Target | What it does |
|---|---|
| `make arxiv` | package the sources arXiv needs into `arxiv.tar.gz` |
| `make format` | rewrite `main.tex` one sentence per line |
| `make logo` | regenerate `figures/ai4g_light.pdf` from its SVG |
| `make clean` | remove build artifacts |

`figures/` holds figures (the lab logo lives there and the title page needs it), `tables/` holds
generated tables, and `references.bib` holds citations. Citations go through `biblatex` and
`biber`: cite with `\citep{key}` or `\citet{key}`, and `\printbibliography` renders the list.
Build output is git-ignored.

The directory is self-contained, so it uploads to Overleaf as is.

`arxiv_collector.py` is a vendored copy of
[arxiv-collector](https://github.com/djsutherland/arxiv-collector) 0.4.1 (BSD 3-clause).
The only local changes are its license header and HTTPS download URLs, so a future version
drops in cleanly.

The rest of this file is the writing contract. Apply it whenever you draft or edit any section.

## Paper structure

Sections run in this order:

1. **Title**
2. **Abstract**
3. **Introduction**: Motivation, Related Work, Gap
4. **Methods**
5. **Results**
6. **Conclusion**
7. **Acknowledgments**
8. **References**
9. **Appendix** (optional)

## Narrative arc

Every paper moves through these seven beats in order:

1. Here's a problem.
2. It's an interesting problem.
3. It's unsolved.
4. Here's my idea.
5. My idea works (evidence).
6. Here's how my approach compares to others.
7. Here's how we can evolve this idea.

## Writing style

- Use American English.
- Use active voice.
- Spell out abbreviations on first use.
- Use adjectives sparingly. Each one earns its place.
- Use colons and em dashes sparingly.
- Keep paragraph formatting simple, and use itemized or enumerated lists only where a list makes the content clearer.
- Use plain text in prose when possible instead of arrows or other decorative symbols.

## Section-by-section guidance

### Abstract

Answer these five questions, in this order:

1. What is the problem you are solving?
2. Why is it an interesting problem?
3. What is the proposed solution?
4. What did you achieve with the solution?
5. What impact will the solution have?

### Introduction

- Open with the problem and why it matters.
- In **Related Work**, survey prior approaches and cite papers making contrary claims where you can. They sharpen the gap.
- State the gap: what prior work leaves unsolved.
- Describe your experiments in one paragraph.

### Methods

- Define inputs, outputs, and notation precisely.

### Results

- Interpret the numbers. Say what they mean, not only what they are.

### Figures

- Give each figure a descriptive caption, labeled axes, and a legend when it shows multiple series.
- Keep diagrams simple and high-contrast. Cut decoration.

### Conclusion

- Focus on the method's **limitations**. Be honest and specific.
- Describe concrete **next steps** rather than vague future work.
