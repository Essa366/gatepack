import pytest

from gatepack.gates.subtitles import check


@pytest.mark.parametrize("ext", ["srt", "vtt"])
def test_missing_separator_before_second_timing(tmp_path, ext):
    path = tmp_path / f"captions.{ext}"
    if ext == "vtt":
        text = "WEBVTT\n\n00:00.000 --> 00:02.000\nA\n00:03.000 --> 00:02.000\nB"
    else:
        text = "1\n00:00:00,000 --> 00:00:02,000\nA\n2\n00:00:03,000 --> 00:00:02,000\nB"
    path.write_text(text, encoding="utf-8")
    findings, _ = check(path)
    assert any(f.level == "FAIL" and f.code == "separator" for f in findings)


@pytest.mark.parametrize("space", [" ", "\t"])
def test_whitespace_line_in_vtt_payload(tmp_path, space):
    path = tmp_path / "captions.vtt"
    path.write_text(f"WEBVTT\n\n00:00.000 --> 00:02.000\nA\n{space}\nB", encoding="utf-8")
    assert check(path) == ([], {"cues": 1})


def test_srt_whitespace_separator_and_literal_arrow(tmp_path):
    path = tmp_path / "captions.srt"
    path.write_text("1\n00:00:00,000 --> 00:00:01,000\nA --> B\n \t\n"
                    "2\n00:00:01,000 --> 00:00:02,000\nC", encoding="utf-8")
    assert check(path) == ([], {"cues": 2})


@pytest.mark.parametrize(("left", "right", "valid"), [
    (" ", " ", True),
    ("\t", "\t", True),
    ("\u00a0", " ", False),
    (" ", "\u00a0", False),
    (" \u00a0 ", "\t", False),
])
def test_webvtt_arrow_delimiters(tmp_path, left, right, valid):
    path = tmp_path / "delimiters.vtt"
    path.write_text(f"WEBVTT\n\n00:00.000{left}-->{right}00:02.000 line:90%\nCaption", encoding="utf-8")
    findings, measured = check(path)
    assert measured["cues"] == 1
    if valid:
        assert not findings
    else:
        assert any(f.level == "FAIL" and f.code == "timing" for f in findings)


@pytest.mark.parametrize("header", [
    "WEBVTT\nKind: captions\nLanguage: en",
    "WEBVTT export\nX-TIMESTAMP-MAP=LOCAL:00:00:00.000,MPEGTS:900000",
])
def test_exporter_headers(tmp_path, header):
    path = tmp_path / "export.vtt"
    path.write_text(header + "\n\n00:00.000 --> 00:01.000\nText", encoding="utf-8")
    assert check(path) == ([], {"cues": 1})


@pytest.mark.parametrize("header", [
    "WEBVTTX\nKind: captions",
    "WEBVTT\nKind: captions\n00:00.000 --> 00:01.000\nLost cue",
    "WEBVTT\nLanguage: en --> 00:01.000",
    "WEBVTT\nUnrecognized line",
])
def test_header_cannot_swallow_cues_or_arbitrary_text(tmp_path, header):
    path = tmp_path / "invalid.vtt"
    path.write_text(header + "\n\n00:02.000 --> 00:03.000\nText", encoding="utf-8")
    findings, _ = check(path)
    assert any(f.level == "FAIL" and f.code == "header" for f in findings)


@pytest.mark.parametrize(("marker", "body"), [
    ("NOTE comment", "Another line"),
    ("STYLE ", "::cue { color: lime; }"),
    ("REGION\t", "id:subtitle"),
])
def test_vtt_metadata_blocks_require_separation(tmp_path, marker, body):
    path = tmp_path / "blocks.vtt"
    block = f"WEBVTT\n\n{marker}\n{body}"
    cue = "\n\n00:05.000 --> 00:06.000\nCaption"
    path.write_text(block + cue, encoding="utf-8")
    assert check(path) == ([], {"cues": 1})

    path.write_text(block + "\n00:03.000 --> 00:02.000\nLost" + cue, encoding="utf-8")
    findings, measured = check(path)
    assert any(f.level == "FAIL" and f.code == "separator" for f in findings)
    assert measured["cues"] == 1


@pytest.mark.parametrize("identifier", ["STYLE", "REGION", "NOTEBOOK"])
def test_vtt_marker_can_be_cue_identifier(tmp_path, identifier):
    path = tmp_path / "identifier.vtt"
    path.write_text(f"WEBVTT\n\n{identifier}\n00:00.000 --> 00:02.000\nCaption", encoding="utf-8")
    assert check(path) == ([], {"cues": 1})


@pytest.mark.parametrize("comment", ["NOTE", "NOTE comment", "NOTE\tcomment"])
def test_vtt_note_is_never_a_cue_identifier(tmp_path, comment):
    path = tmp_path / "note.vtt"
    path.write_text(f"WEBVTT\n\n{comment}\n00:00.000 --> 00:02.000\nCaption", encoding="utf-8")
    findings, measured = check(path)
    assert [(f.level, f.code) for f in findings] == [("FAIL", "separator"), ("WARN", "empty")]
    assert measured["cues"] == 0
