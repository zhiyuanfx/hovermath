#!/usr/bin/env python3
"""Check the content of a hovermath page without opening it.

    python3 check_page.py page.html

It reads the block between the CONTENT START and CONTENT END markers and reports:
  errors    a {{key}} or \\sym{key} that is not in SYM; a symbol whose kind is not in KINDS; a symbol whose
            ref is not a section id; a repeated equation tag or section id; a figure file that is missing
            (and not embedded).
  warnings  a symbol that is never used; a formula whose braces do not balance.

It does not render the math. Formulas that KaTeX cannot render show up when the page is opened: the page then
lists its problems in a red box at the top (and in the browser console).

The exit status is 1 if there are errors. Needs only the Python standard library.
"""
import pathlib
import re
import sys

CONTENT = re.compile(r"/\* ==== CONTENT START ====.*?/\* ==== CONTENT END ==== \*/", re.S)
ENTRY = re.compile(r'(?m)^\s*(?:"([^"]+)"|\'([^\']+)\'|([A-Za-z_$][\w$]*))\s*:\s*\{')


def strip_comments(js):
    """The script text without // and /* */ comments. Strings and template strings are kept as they are."""
    out, i, quote = [], 0, None
    while i < len(js):
        ch = js[i]
        if quote:
            out.append(ch)
            if ch == "\\" and quote != "`" and i + 1 < len(js):
                out.append(js[i + 1])
                i += 1
            elif ch == quote:
                quote = None
        elif js.startswith("//", i):
            j = js.find("\n", i)
            i = len(js) if j < 0 else j
            continue
        elif js.startswith("/*", i):
            j = js.find("*/", i + 2)
            i = len(js) if j < 0 else j + 2
            continue
        else:
            if ch in "\"'`":
                quote = ch
            out.append(ch)
        i += 1
    return "".join(out)


def const_block(content, name):
    """Text of `const NAME = {...};` or `[...]`, found by matching brackets (strings are skipped)."""
    m = re.search(r"const\s+%s\s*=\s*([\[{])" % name, content)
    if not m:
        return None
    opener = m.group(1)
    closer = "}" if opener == "{" else "]"
    depth, i, quote = 0, m.end() - 1, None
    while i < len(content):
        ch = content[i]
        if quote:
            if ch == "\\" and quote != "`":
                i += 1
            elif ch == quote:
                quote = None
        elif ch in "\"'`":
            quote = ch
        elif ch == opener:
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return content[m.end():i]
        i += 1
    return None


def entries(block):
    """Top-level `key: { ... }` entries of an object literal, as {key: text}."""
    out, hits = {}, list(ENTRY.finditer(block))
    for n, m in enumerate(hits):
        key = m.group(1) or m.group(2) or m.group(3)
        out[key] = block[m.end():hits[n + 1].start() if n + 1 < len(hits) else len(block)]
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    page = pathlib.Path(sys.argv[1])
    html = page.read_text(encoding="utf-8")
    m = CONTENT.search(html)
    if not m:
        sys.exit("No CONTENT START / CONTENT END markers found: is this a hovermath page?")
    content = strip_comments(m.group(0))
    errors, warnings = [], []

    blocks = {name: const_block(content, name) for name in ("DOC", "KINDS", "SYM", "SECTIONS")}
    for name, b in blocks.items():
        if b is None:
            errors.append(f"const {name} is missing from the content block")
    if errors:
        report(page, errors, warnings, {})
    kinds = entries(blocks["KINDS"])
    syms = entries(blocks["SYM"])
    sections = blocks["SECTIONS"]

    section_ids = re.findall(r'\{\s*id:\s*"([^"]+)"\s*,\s*(?:num:\s*"[^"]*"\s*,\s*)?title:', sections)
    for sid in sorted({s for s in section_ids if section_ids.count(s) > 1}):
        errors.append(f'section id "{sid}" is used more than once')

    for key, body in syms.items():
        k = re.search(r'\bkind:\s*"([^"]+)"', body)
        if not k:
            errors.append(f"symbol {key} has no kind")
        elif k.group(1) not in kinds:
            errors.append(f'symbol {key} has kind "{k.group(1)}", which is not in KINDS')
        r = re.search(r'\bref:\s*"([^"]+)"', body)
        if r and r.group(1) not in section_ids:
            errors.append(f'symbol {key} points to section "{r.group(1)}", which does not exist')
        if not re.search(r"\bdef:", body):
            warnings.append(f"symbol {key} has no definition (def)")

    used = set(re.findall(r"\{\{(\w+)\}\}", content)) | set(re.findall(r"\\sym\{(\w+)\}", content))
    for key in sorted(used - set(syms)):
        errors.append(f"{{{{{key}}}}} or \\sym{{{key}}} is used, but SYM has no entry {key}")
    listed = set(re.findall(r'"(\w+)"', " ".join(re.findall(r"keys:\s*\[([^\]]*)\]", sections))))
    for key in sorted(listed - set(syms)):
        errors.append(f'a symbol list names "{key}", but SYM has no entry {key}')
    for key in sorted(set(syms) - used - listed):
        if not re.search(r"\bword:", syms[key]):
            warnings.append(f"symbol {key} is defined but never used")

    tags = re.findall(r'\btag:\s*"([^"]+)"', sections)
    for t in sorted({t for t in tags if tags.count(t) > 1}):
        errors.append(f'equation tag "{t}" is used more than once')

    for tex in re.findall(r"\btex:\s*R`([^`]*)`", content):
        plain = re.sub(r"\$\{[^}]*\}", "", tex.replace("\\{", "").replace("\\}", ""))
        if plain.count("{") != plain.count("}"):
            warnings.append(f"braces do not balance in: {tex[:70]}")

    embedded = set(re.findall(r'"([^"]+)":\s*"data:', html))
    for a, b in re.findall(r"""\bsrc:\s*(?:"([^"]+)"|'([^']+)')""", sections):
        src = a or b
        if re.match(r"(?:https?:|data:)", src) or src in embedded:
            continue
        if not (page.parent / src).is_file():
            errors.append(f"figure file not found: {src}")

    stats = {"symbols": len(syms), "kinds": len(kinds), "sections": len(section_ids), "equation tags": len(tags),
             "explanations": len(re.findall(r"\bexpl:", sections)), "added by us": len(re.findall(r"\badded:\s*true", sections)),
             "figures": len(re.findall(r"\bfig:\s*\{", sections)), "tables": len(re.findall(r"\btable:\s*\{", sections))}
    report(page, errors, warnings, stats)


def report(page, errors, warnings, stats):
    print(page)
    if stats:
        print("  " + ", ".join(f"{v} {k}" for k, v in stats.items()))
    for w in warnings:
        print("  warning:", w)
    for e in errors:
        print("  ERROR:", e)
    print(f"  {len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
