# Markdown Frontmatter Check (GitHub composite action)

Fails your CI when markdown files are missing required YAML frontmatter keys, or when a key has the wrong type.
Python standard library only. No network calls. MIT licence.

## Scope (what it does and does not check)

- Frontmatter must start on line 1 with `---` and close with a later `---` line.
- Only **flat top-level keys** are understood: `key: value` scalar lines and `- item` list blocks.
- Nested YAML maps, anchors and multi-line scalars are **not** supported.
- Types: `string` (non-empty), `bool` (`true`/`false`), `date` (`YYYY-MM-DD`, must be a real calendar date), `list` (non-empty).

## Usage

```yaml
- uses: OWNER/REPO@v1          # replace with the published repo once it exists
  with:
    files: 'content/**/*.md'
    required: 'title:string,date:date,tags:list'
```

Exit behaviour: the step fails (exit 1) if any problem is found, so the CI job goes red. A usage error (bad type name, no files matched) exits 2.

Each problem prints as `FAIL <file>:<line>: <message>`, for example:

```
FAIL content/post.md:3: key 'date' is not a real calendar date
FAIL content/post.md: missing required key 'tags'
checked 2 file(s), 1 problem(s)
```

## Run it locally (without GitHub)

```
python check_frontmatter.py "content/**/*.md" "title:string,date:date,tags:list"
```

## Tests

```
python tests/test_check_frontmatter.py
```

Covers good and bad fixtures: missing frontmatter, unclosed block, missing key, empty list, empty title, impossible date (2026-02-30), whole-directory failure, no-match usage error, and unknown type.

## Known limits

- The composite action wrapper (`action.yml`) has not yet been run inside a GitHub Actions runner. The Python core is tested; the shell wrapper is not. Treat the action as unverified in CI until a workflow run is recorded.
- Tested only on synthetic fixtures. Compatibility with real Hugo, Jekyll or Obsidian sites beyond flat keys is not established.

## Licence

MIT. See LICENSE.
