#!/usr/bin/env python3
"""Check that markdown files start with a YAML frontmatter block containing required flat keys.

Scope (deliberately narrow, documented in README):
  * frontmatter must start on line 1 with '---' and end with a later '---' line
  * only top-level 'key: value' scalar lines and '- item' list blocks are understood
  * types: string | bool | date (YYYY-MM-DD) | list
Exit code 0 = all files pass, 1 = at least one problem, 2 = usage error.
"""
import datetime
import glob
import os
import re
import sys

KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s*(.*))?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TYPES = {"string", "bool", "date", "list"}


def parse_frontmatter(text):
    """Return (data, error). data maps key -> value (str | list); line numbers in data['__lines__']."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "missing frontmatter (file must start with '---')"
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, "frontmatter not closed (no closing '---')"
    data, lines_map, current = {}, {}, None
    for idx in range(1, end):
        raw = lines[idx]
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith((" ", "\t")) or raw.startswith("- "):
            stripped = raw.strip()
            if current is not None and isinstance(data.get(current), list) and stripped.startswith("- "):
                data[current].append(stripped[2:].strip().strip('"\''))
            continue
        m = KEY_RE.match(raw)
        if not m:
            return None, f"line {idx + 1}: not a 'key: value' line: {raw.strip()!r}"
        key, value = m.group(1), (m.group(2) or "").strip()
        current = key
        lines_map[key] = idx + 1
        if value == "":
            data[key] = []
        else:
            data[key] = value.strip('"\'')
    data["__lines__"] = lines_map
    return data, None


def check_value(value, expected):
    if expected == "list":
        return isinstance(value, list) and len(value) > 0, "must be a non-empty list"
    if isinstance(value, list):
        if len(value) == 0:
            # 'key:' with nothing after it parses as an empty list; for scalar types it is an empty value
            return False, "must not be empty"
        return False, "must be a scalar, got a list"
    if expected == "bool":
        return value.lower() in ("true", "false"), "must be true or false"
    if expected == "date":
        if not DATE_RE.match(value):
            return False, "must be YYYY-MM-DD"
        try:
            datetime.date.fromisoformat(value)
        except ValueError:
            return False, "is not a real calendar date"
        return True, ""
    return value != "", "must not be empty"


def check_file(path, required):
    """required: list of (key, type). Returns list of problem strings."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    data, err = parse_frontmatter(text)
    if err:
        return [f"{path}: {err}"]
    problems = []
    for key, expected in required:
        if key not in data:
            problems.append(f"{path}: missing required key '{key}'")
            continue
        ok, why = check_value(data[key], expected)
        if not ok:
            problems.append(f"{path}:{data['__lines__'].get(key, 1)}: key '{key}' {why}")
    return problems


def parse_required(spec):
    required = []
    for item in spec.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" in item:
            key, typ = (p.strip() for p in item.split(":", 1))
        else:
            key, typ = item, "string"
        if typ not in TYPES:
            raise ValueError(f"unknown type '{typ}' for key '{key}' (allowed: {sorted(TYPES)})")
        required.append((key, typ))
    if not required:
        raise ValueError("no required keys given")
    return required


def main(argv):
    if len(argv) != 3:
        print("usage: check_frontmatter.py <glob> <required keys, e.g. 'title:string,date:date,tags:list'>")
        return 2
    try:
        required = parse_required(argv[2])
    except ValueError as e:
        print(f"error: {e}")
        return 2
    files = sorted(p for p in glob.glob(argv[1], recursive=True) if os.path.isfile(p))
    if not files:
        print(f"no files matched {argv[1]!r}")
        return 2
    problems = []
    for f in files:
        problems.extend(check_file(f, required))
    for p in problems:
        print("FAIL " + p)
    print(f"checked {len(files)} file(s), {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
