---
name: hovermath
description: Turn a math-heavy source into one interactive HTML reading page where every symbol shows its definition on hover, equation numbers preview their equations, and each group of equations is followed by its explanation. The source can be a paper or other PDF, a Markdown or LaTeX file, an optimization model, or a model worked out in the conversation. Use when the user asks for a hover page, an interactive or easier-to-read version of a paper or model, a reading companion, or says the symbols in a document are hard to keep track of.
---

# hovermath

Reading math is slow when every line sends the reader back to a symbol table. A hovermath page removes that
trip. It is one HTML file in which:

- every symbol, and every other name the author defines, shows its definition on hover and can be pinned with a click;
- an equation number in the text previews the equation on hover and jumps to it on a click;
- each small group of equations is followed directly by its explanation;
- a contents panel, a text-size control, a symbol-color switch and a light/dark switch are always at hand.

The skill is about this presentation. It puts few rules on the content: the page says what the source says.

## Files in this skill

| File | Use |
| --- | --- |
| `assets/template.html` | The page engine with a short placeholder document. Copy it, then replace the content block. |
| `references/format.md` | The content format: every field and block type, with examples. Read it before writing a page. |
| `scripts/check_page.py` | Checks a page's content without a browser. |
| `scripts/crop_figure.py` | Cuts figures out of a PDF (needs PyMuPDF). |
| `scripts/embed_figures.py` | Puts the figure files inside the page, so the page is one file. |
| `scripts/make_offline.py` | Makes a copy of a page that opens without internet. |
| `examples/two-stage-ordering.html` | A finished page for a toy model. |

## Steps

1. **Read the whole source.** For a PDF, read the text and look at the pages, since extracted text loses
   most of the math. For a model from the conversation, collect what was agreed and nothing more. If it is
   unclear which part of a long source the user wants, ask; otherwise do all of it.
2. **Copy `assets/template.html`** to the output file. Name it after the source and put it next to the
   source, unless the user names a place.
3. **Replace the content block**, the part between the `CONTENT START` and `CONTENT END` markers, following
   `references/format.md`. It has four parts: `DOC` (title and header), `KINDS` (the kinds of symbols in this
   document), `SYM` (one entry for everything the author defines) and `SECTIONS` (the document itself). Do
   not change anything outside the markers.
4. **Add the figures.** Save each one in a `figures/` folder next to the page and name it in a figure block.
5. **Check the page.** Run `python3 scripts/check_page.py page.html` and fix what it reports. If you can open
   the page in a browser, do so: a red box at the top lists formulas that do not render and symbol keys that
   do not exist. Then hover a few symbols and equation numbers, and look at the page in the dark theme and
   at phone width.
6. **Embed the figures**: `python3 scripts/embed_figures.py page.html`. This is the default, see Options.
7. **Hand over one file**: the page, with its figures embedded and the math renderer loaded online. Do not
   also make an offline copy or keep a figures folder unless the user asked for it.
8. **Tell the user** where the page is, what you added that is not in the source (explanations, notes,
   drawn figures), anything in the source you could not read with confidence, and, in one sentence, that an
   offline copy or a separate figures folder is available if they want one.

## Content rules

**Keep the source as it is given.** Same order, same section numbers, same wording, same equations with the
same equation numbers. Do not paraphrase, shorten, translate or reorganize unless the user asks. The
departures allowed without asking are small: fixing an obvious typo or grammar slip, moving an explanation
under its equations (below), a Reader's note, and an added explanation where one is missing. If the user asks
for something else, such as a condensed version or their own structure, do what they ask.

When the source is someone else's published work, tell the user once that the page reproduces its text, in
case they plan to post the page publicly.

**What is hoverable.** Everything the author defines in this document: sets, indices, parameters, variables,
functions, and also names written as plain words, such as a named index (TF), a case label (B0) or a named
method. General abbreviations and notation of the field, which the document only uses, are not hoverable.

- Write each definition in the source's own words. If the source uses a symbol without defining it, say so
  in the definition and give the meaning you read from where it is used.
- A variant of a symbol (another index, a star, a hat) hovers to the same entry; see `\sym` in the format.
- Choose the kinds of symbols for this document, and give a color only to the few kinds a reader must tell
  apart at a glance, for example first-stage decisions, second-stage decisions and uncertain quantities.

**Equations.** Reproduce every equation exactly, in TeX that KaTeX renders, and compare each with the source
before moving on. Keep the source's equation numbers as tags. If the source has no numbers and the text needs
to point at equations, as with a model from a conversation, number them.

**Groups and explanations.** Do not print a long model first and all its explanations afterwards. Split it
into small groups of related lines and put each group's explanation directly under it. When the source
explains its lines after the whole model, move each explanation under its lines with the wording unchanged.
One explanation per group is enough.

**Adding explanations.** Be sparing. Add an explanation of your own only when the source gives none for a
group, or one too thin for a reader to follow, or when the user asks for more. Keep it short, say what the
lines mean, and do not repeat what a neighboring sentence already says. Always mark it as added
(`added: true`): the page then shows it with a differently colored bar and lists that bar in the legend as
"Explanation added by us". If the user asks for every group to be explained, do that.

**Reader's notes.** Use a note for a clarification that is yours: a typo or notation quirk in the source, or
why a step works. Keep them few.

**Figures.** Use each figure as it is given: crop it from the PDF (`scripts/crop_figure.py`) or use the image
file the user provides, without its caption, and give the caption as text. Do not redraw a figure unless the
user asks or no image exists; if you draw one, keep it simple and say that you drew it.

**Tables.** Rebuild a table as a table block when it is a plain grid of text and numbers; author-defined
names in its cells then hover like anywhere else. Crop it as a figure when its layout is too irregular to
rebuild faithfully.

**Do not add claims.** No results, data, calibration or solver runs that the source does not report.

## Options

Make the default unless the user asks for the alternative. Mention that the alternatives exist when you hand
over the page; do not produce them unasked. If you need an offline copy only to check the page in a browser
that has no internet, make it in a temporary place and delete it afterwards.

| | Default | Alternative |
| --- | --- | --- |
| Figures | Embedded in the page, so it is a single file that can be sent anywhere. Embedding adds about a third to the size of the image files. | Keep a `figures/` folder next to the page: skip step 6, or run `embed_figures.py page.html --clear`. The HTML file stays small, and the folder must travel with it. |
| Math renderer | Loaded from a public CDN when the page opens, so viewing needs internet. | An offline copy: `python3 scripts/make_offline.py page.html` writes `page.offline.html` with KaTeX inside, about 0.65 MB larger. The script needs internet once, unless a copy of KaTeX is in `assets/katex/`. |

## Notes on kinds of input

- **PDF paper.** Text extraction gives the prose; type the math yourself from the page. Use
  `crop_figure.py captions` to find figures and `crop_figure.py page` to see a page. A zoom of 3 is sharp
  enough for a crop.
- **Markdown or LaTeX.** Expand the author's own macros into plain TeX, and replace commands KaTeX does not
  have. Numbered environments become tags.
- **A model or idea from the conversation.** There is no layout to follow, so use a plain one: setting, sets
  and indices, parameters, variables, objective, constraints, then anything else that was discussed. Write
  only what was said or clearly implied, and ask about gaps instead of filling them.
