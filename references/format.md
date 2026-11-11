# The content format

A hovermath page is `assets/template.html` with its content block replaced. The content block is the part of
the script between these two markers:

```js
/* ==== CONTENT START ==== ... */
const DOC = { ... };
const KINDS = { ... };
const SYM = { ... };
const SECTIONS = [ ... ];
/* ==== CONTENT END ==== */
```

Everything outside the markers is the engine and stays as it is. `examples/two-stage-ordering.html` is a
complete page to copy from.

## Writing text and formulas

Strings are written as `` R`...` `` (JavaScript `String.raw`), so a backslash is typed once: `` R`\sum_i x_i` ``.

- A string must not contain a backtick, and `${` starts a JavaScript insertion, so do not type it literally.
- **Formulas** are TeX, rendered by KaTeX. Use only commands KaTeX supports.
- **`{{key}}`** in a formula prints the symbol `SYM[key]` and makes it hoverable.
- **`\sym{key}{tex}`** prints `tex` and hovers to `SYM[key]`. Use it for a variant of a symbol: another index
  (`\sym{x}{x_{t+1}}`), a star or hat (`\sym{lam}{\lambda^*}`), or the bare letter (`\sym{x}{x}`).
- A symbol inside braces needs three: `\sum_{{{i}}\in{{I}}}` is `\sum_{` + `{{i}}` + `\in` + `{{I}}` + `}`.
- **Text** uses `\( ... \)` for inline math (with `{{key}}` and `\sym` as in formulas), `**bold**` and
  `[label](url)`.
- **Equation references.** A parenthesized equation tag in text, such as `(3b)`, becomes a link to that
  equation with a preview on hover. So does the `id` of an equation block, such as `(MP)`, and the common
  stem of lettered tags: `(3)` previews (3a), (3b), ... together. Nothing needs to be marked; write the text
  normally.

To avoid repeating a long piece of TeX, define a constant between `SYM` and `SECTIONS` and insert it:

```js
const sumS = R`\sum_{{{s}}\in{{S}}}`;
// later, inside a formula:  R`${sumS}{{pi}}{{z}}`
```

## DOC

```js
const DOC = {
  title: "Full title",
  short: "Short title",      // contents panel and browser tab; defaults to title
  eyebrow: "Reading page",   // small line above the title (optional)
  authors: "A. Author, B. Author",
  source: "Journal, year, DOI; or a file name; or where the model comes from",
  links: [{ label: "DOI page ↗", href: "https://doi.org/..." }],
  note: R`Boxed note under the header, for example how the page was made.`,
  footer: "Line at the bottom of the page.",
  figZoom: 3,                // zoom at which the figures were cropped from a PDF
};
```

Only `title` is required. `source`, `note` and `footer` may contain inline math and links.

## KINDS

The kinds of symbols in this document. Each symbol's tooltip shows its kind, and the glossary at the end of
the page is grouped by kind, in this order.

```js
const KINDS = {
  set: { label: "Set", color: "purple" },
  idx: { label: "Index" },
  par: { label: "Parameter" },
  rnd: { label: "Uncertain quantity", color: "orange" },
  st1: { label: "First-stage decision", color: "blue" },
  st2: { label: "Second-stage decision", color: "green" },
  fn:  { label: "Computed value" },
  term: { label: "Defined term" },
};
```

- The keys are yours to choose. Fit the kinds and labels to the document.
- `color` is one of `blue`, `green`, `orange`, `pink`, `purple`, or left out for plain text.
- Color only the few kinds a reader must tell apart at a glance. The legend lists the colored kinds that are
  in use, then "Other symbols".

## SYM

One entry for everything the author defines.

```js
const SYM = {
  x:  { tex: R`x_i`, kind: "st1", dom: R`x_i\ge0`, def: R`Quantity of item \(i\) ordered.`, ref: "model" },
  FR: { tex: R`\mathrm{FR}`, word: "FR", kind: "fn", def: R`Fill rate (2): the expected share of demand served.`, ref: "service" },
  Bk: { tex: R`\mathrm{B}0,\dots,\mathrm{B}8`, word: ["B0", "B1", "B2"], kind: "term", def: R`Budget cases of the study.` },
};
```

| Field | Meaning |
| --- | --- |
| `tex` | How the symbol prints. This is what `{{key}}` inserts. |
| `kind` | A key of `KINDS`. |
| `def` | The definition, shown in the tooltip and the glossary. Text, with inline math allowed. |
| `dom` | Domain, range or defining formula, in TeX (optional). Shown under the definition. |
| `ref` | The `id` of the section where the symbol is defined (optional). The tooltip links there. |
| `word` | A plain word, or a list of words, that the text uses for this entry (optional). |

- Keys are letters, digits and underscores. A key is only a handle; readers never see it.
- **`word`** is for names the author defines and the text writes as ordinary words, such as an index called
  TF or the case labels B0 to B8. Every whole-word occurrence in paragraphs, explanations, notes, table cells
  and captions becomes hoverable. Do not give a `word` to a general abbreviation of the field.
- A definition may use `{{key}}` for other symbols. They print without hover inside a tooltip and with hover
  in the glossary.

## SECTIONS

```js
const SECTIONS = [
  { id: "intro", num: "I", title: "Introduction", blocks: [ ... ] },
  { id: "s2", num: "II", title: "Formulation", blocks: [ ... ], subs: [
    { id: "s2a", num: "II-A", title: "Model", blocks: [ ... ] },
  ]},
];
```

- `id` must be unique and usable as an HTML id (letters, digits, hyphens). It is the link target for the
  contents panel and for `ref` in `SYM`.
- `num` is the number as the source prints it (optional).
- A section may have `blocks`, `subs` (subsections, one level), or both.
- A symbol glossary is added after the last section automatically.

## Blocks

### Paragraph

```js
{ p: R`Text with inline math \({{x}}\), **bold** and a reference to (1a).` }
```

### Equations

```js
{ id: "TS", eqs: [
  { tag: "1a", tex: R`\max\ -{{c}}{{x}}+\sum_{{{s}}\in{{S}}}{{pi}}({{p}}{{z}}-{{r}}{{y}})` },
  { expl: R`(1a) Expected profit.` },
  { tag: "1b", tex: R`{{z}}\le{{d}},\quad\forall{{s}}\in{{S}}` },
  { tag: "1c", tex: R`{{z}}\le{{x}}+{{y}},\quad\forall{{s}}\in{{S}}` },
  { expl: R`Sales cannot exceed demand or the units on hand.`, added: true },
]}
```

- Each row with `tex` is one displayed line. `tag` is its equation number, printed at the right in
  parentheses; leave it out for an unnumbered line.
- For a formula that runs over several lines under one number, use `\begin{aligned} ... \end{aligned}` in one row.
- A row with `expl` is an explanation of the rows above it. Put it directly after the group it explains.
- `added: true` marks an explanation that is not from the source. It gets the colored bar and the legend
  entry "Explanation added by us". Without it, the bar is gray: "Explanation from the source".
- `id` (optional) names the whole block, such as a model called (TS). Writing `(TS)` in text then links to
  the block and previews all its rows.
- Do not use `\tag` or `\label` inside `tex`.

### Explanation as its own block

```js
{ expl: R`Explanation of the equation block just above.`, added: true }
```

The same as an `expl` row, for use between blocks.

### Reader's note

```js
{ note: R`The source prints \(\lambda_b\) here where \(\lambda_t\) is meant.` }
{ note: R`...`, label: "Remark" }
```

A boxed note for clarifications that are not part of the source. `label` replaces the heading "Reader's note".

### Figure

```js
{ fig: { n: "3", src: "figures/fig03.png", cap: R`Caption as printed, with math \({{x}}\) if needed.` } }
```

| Field | Meaning |
| --- | --- |
| `src` | Image file, relative to the page. PNG, JPEG, GIF, SVG or WebP. |
| `n` | Figure number. The label is "Fig. n." |
| `label` | Replaces the label, for example `"Figure 3:"`; `""` removes it. |
| `cap` | Caption text. Author-defined words in it are hoverable. |
| `zoom` | Zoom this image was cropped at, if different from `DOC.figZoom`. |
| `width` | A CSS width such as `"30em"`, for images that are not PDF crops (screenshots, drawings). |

A crop is shown at its printed size and grows with the text-size control. Crop the figure without its
caption. After `scripts/embed_figures.py` has run, the image data is stored at the end of the page and the
figure block is unchanged.

### Table

```js
{ table: { no: "TABLE 1", title: "Expected profit and FR of five regular orders", cls: "num",
  head: [[R`Regular order \({{x}}\)`, "Expected profit", "FR"]],
  rows: [
    ["60", "402", "0.814"],
    ["80", "462", "0.943"],
  ]}}
```

- `head` is a list of header rows; `rows` is the body. A cell is a string (text with inline math allowed), or
  `{ t: "text", cs: 3 }` to span 3 columns, or `{ t: "text", rs: 2 }` to span 2 rows.
- `cls: "num"` right-aligns every column except the first, for numeric tables.
- `no` and `title` form the caption (both optional).

A two-row header:

```js
head: [[{ t: "SF", rs: 2 }, { t: "B0", cs: 2 }, { t: "B3", cs: 2 }], ["TF", "EDF", "TF", "EDF"]],
```

### Lists

```js
{ ul: [R`First item.`, R`Second item with \({{x}}\).`] }
{ ol: [R`Step one.`, R`Step two.`] }
```

### Symbol list

```js
{ nomen: [
  { title: "Sets and indices", keys: ["S", "s"] },
  { title: "Parameters", keys: ["c", "r", "p"] },
]}
```

A nomenclature table built from `SYM`: each key is shown with its definition. Use it where the source has a
notation section or symbol table, in the source's grouping and order.

### Keywords and small print

```js
{ kw: "robust optimization, cutting planes", label: "Index Terms" }   // label defaults to "Keywords"
{ hint: R`Small gray text, for a remark about the page itself.` }
```

## Checking

`python3 scripts/check_page.py page.html` reports symbol keys that do not exist, kinds that are not in
`KINDS`, `ref`s that point nowhere, repeated tags or ids, and missing figure files. It warns about symbols
that are never used and formulas with unbalanced braces.

It does not render the math. When the page is opened in a browser, formulas that KaTeX rejects appear in red,
and a red box at the top of the page lists every problem found.
