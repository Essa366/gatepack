# Contributing

Thank you for helping. The project grows one gate at a time, and a new gate is the most useful
contribution. Fixes to existing rules, docs and tests are just as welcome.

## Ground rules

1. **One gate = one pull request.** Do not bundle several gates; it makes review slow.
2. **Cite the rule.** Link the platform's help page or the standard. If the threshold is your own
   judgment, say so and mark findings `heuristic`. An anonymised excerpt of a rejection notice is also
   a valid source; remove names, titles and account details first.
3. **Include a PASS file and a FAIL file**, small and reproducible (see `scripts/make_fixtures.py`).
4. **Local files only.** No gate may log in, scrape, upload or publish. No network calls.
5. **No new required dependencies.** Optional extras are fine when the gate needs them.
6. Keep messages plain: say what was measured, the limit, and what to do.

## Workflow

You need Python 3.10 or newer, and ffmpeg (with ffprobe) for the audio and video gates:
`sudo apt-get install ffmpeg`, `brew install ffmpeg`, or `winget install Gyan.FFmpeg` on Windows.

macOS and Linux:

```bash
git clone https://github.com/Essa366/gatepack && cd gatepack
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
ffmpeg -version && ffprobe -version
pytest
```

Windows (PowerShell):

```powershell
git clone https://github.com/Essa366/gatepack; cd gatepack
py -m venv .venv; .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
ffmpeg -version; ffprobe -version
pytest
```

Without ffmpeg the media tests are skipped, not failed; CI sets `GATEPACK_REQUIRE_TOOLS=1` so they must
run there. To work on one gate: `pytest -k my-gate`. Start a gate with `gatepack new my-gate`; it reports
ERROR until you replace the TODO in `check()`. If your gate needs a new executable or Python module, list
it in `requires=` (modules also go in `REQUIREMENT_MODULES` in `core.py`) so tests skip cleanly without it.

Then open a pull request with the template filled in. CI runs the tests on Linux, macOS and Windows,
builds the package, and fails if the pull request adds more than one gate module.

Looking for something to start with? See [docs/first-issues.md](docs/first-issues.md) or the issues
labelled `good first issue`.

## Reporting a wrong rule

Platforms change their rules. If a gate disagrees with the platform's current page, open an issue with
the link and the sentence that changed. That is the fastest fix we can make.

## Review

Maintainers aim to answer every pull request and issue within 24 hours on working days. Contributors
are credited in the release notes of the version that ships their gate.

## Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).
