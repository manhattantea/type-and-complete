# Conversational prose, Python `#` comments, and 5–20% convenience Scaffolds

Status: accepted

We use `CodingTemplateExamples`-style conversational prose, `#` comments instead of Python `"""..."""` explanatory docstrings, zero `"Prompt"` or `"Worked anchor"` labels, zero Markdown formatting inside source comments, and a flexible ~5–20% starter Scaffold across `odin_how_to/`, `python_how_to/`, and `tracy_how_to/`.

## Considered Options

- Keep Python `"""..."""` module and function docstrings with strict 10% Scaffolds and numbered `Prompt N:` / `Worked anchor:` checklists.
- Switch completely to pre-written runnable examples like `CodingTemplateExamples/how_to/`, removing all hands-on open Drills.
- Keep open Drills and ~5–20% starter convenience Scaffolds while writing all explanations in plain conversational prose (`#` in Python, compact `/* ... */` and `//` in Odin), with 1 blank line after `proc() {` / `def ...:` openings, bottom `main` in multi-section Primers, Feynman immediate keyword explanations, and concrete hypothetical scenarios.

## Consequences

- Long Python `"""..."""` string literals render in low-contrast string colors in the IDE and sit in runtime `__doc__` attributes, so prose moves to `#` comment blocks everywhere except files explicitly demonstrating string literals or docstrings.
- Retiring `"Prompt"` and numbered checklists prevents formulaic textbook dumps and spoiler recipes, relying on natural prose Drills (graduated from explicit convenience snippets down to open synthesis tasks) to steer both the learner and IDE autocompletion.
- Thin Primers (previously ~50–80 lines) expand toward multi-section `~150–300+` line units with higher everyday drill density, while avoiding obscure flag trivia.
