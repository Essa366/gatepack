# Subtitle timing

Run `gatepack check subtitles captions.vtt` on a local UTF-8 file (optional BOM). For WebVTT the gate checks the header, timestamp format, ordered starts, and positive durations. For SubRip it checks the analogous conventions, including numeric cue indices and comma milliseconds. SRT findings are heuristic.

Overlapping subtitles are valid in WebVTT. Set `--overlaps reject` for deliveries requiring distinct intervals. Set `--max-line-length 42` to warn on longer source lines, including markup. Both policies are optional heuristics. Cue styling, inline markup and positioning settings are outside this timing check.

The header also accepts exporter metadata lines beginning with `Kind:`, `Language:` or `X-TIMESTAMP-MAP=` before the empty separator. HLS timestamp mapping and synchronization are outside the scope of this gate.

Source: [W3C WebVTT cue timings](https://www.w3.org/TR/webvtt1/#webvtt-cue-timings).
