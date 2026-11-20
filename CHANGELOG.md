# Changelog

## Unreleased

- CI: actions/checkout and actions/setup-python v7 (Node 24); a job that builds the sdist and wheel and runs `twine check`; a check that a pull request adds at most one gate
- Issue forms for new gates and bugs, a pull request template that asks for the rule source and PASS/FAIL fixtures
- README: terminal demo rendered from real runs (`scripts/make_demo_svg.py`)

## 0.1.0 (unreleased)

First version, eight gates:

- KDP: `kdp-metadata`, `kdp-cover-safezone`, `kdp-pagecount`, `epub`
- Audio and video (ffmpeg): `dead-air`, `freeze`, `loudness`, `tail`
- CLI: `gatepack list`, `gatepack check <gate> <files>`, `gatepack new <gate-id>`; JSON output; exit codes
- Claude Code plugin with a `gatepack` skill
