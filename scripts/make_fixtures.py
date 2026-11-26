"""Regenerate every test fixture from code, so reviewers can see exactly what each file contains.

    python scripts/make_fixtures.py               (all groups; needs ffmpeg on PATH and Pillow)
    python scripts/make_fixtures.py covers epub   (only these groups: metadata, pagecount, covers, epub, media)

Fixtures live in tests/fixtures/<gate-id>/{pass,fail}/. A file may have a sidecar
<file>.args.json with the gate options the test passes. Media files are tiny on purpose.
"""
from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "tests" / "fixtures"


def put(gate: str, kind: str, name: str, data: bytes | str | None = None, args: dict | None = None) -> Path:
    path = ROOT / gate / kind / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if data is not None:
        path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
    if args:
        Path(f"{path}.args.json").write_text(json.dumps(args, indent=2) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------- kdp-metadata
def metadata() -> None:
    def j(d):
        return json.dumps(d, indent=2, ensure_ascii=False) + "\n"

    put("kdp-metadata", "pass", "paperback_word_search.json", j({
        "format": "paperback", "trim": "8.5x11",
        "title": "Quiet Garden Word Search",
        "subtitle": "120 Large Print Puzzles for Adults",
        "description": "<p>120 large print word search puzzles on garden themes, one per page, "
                       "printed on 8.5 x 11 inch pages with solutions at the back.</p>",
        "keywords": ["large print word search", "garden puzzles for adults", "word find for seniors"],
    }))
    put("kdp-metadata", "pass", "ebook_prose.json", j({
        "format": "kindle ebook",
        "title": "The Patient Gardener",
        "subtitle": "Growing Vegetables in Small Spaces",
        "description": "<p>A practical guide to growing vegetables on balconies and in small yards.</p>",
        "keywords": ["balcony vegetable garden", "small space gardening"],
    }))
    put("kdp-metadata", "fail", "ebook_coloring_book.json", j({
        "format": "kindle ebook",
        "title": "Ocean Animals Coloring Book",
        "subtitle": "50 Designs for Kids",
        "description": "<p>50 coloring pages with sea creatures.</p>",
        "keywords": ["ocean coloring"],
    }))
    put("kdp-metadata", "fail", "trademark_and_working_note.json", j({
        "format": "paperback", "trim": "6x9",
        "title": "Minecraft Builder Notebook",
        "subtitle": "TODO pick a subtitle",
        "description": "<p>The bestselling notebook. Visit www.example.com</p>",
        "keywords": ["notebook"],
    }))
    put("kdp-metadata", "fail", "trim_and_count_mismatch.json", j({
        "format": "paperback", "trim": "8.5x11",
        "title": "Mandala Coloring Book",
        "subtitle": "100 Designs for Relaxation",
        "description": "<p>Printed on 6 x 9 inch pages, with 50+ designs.</p>",
        "keywords": ["mandala coloring"],
    }))


# ---------------------------------------------------------------- kdp-pagecount
def pdf(pages: int, w_in: float, h_in: float) -> bytes:
    """A valid, uncompressed PDF with `pages` blank pages."""
    w, h = round(w_in * 72, 2), round(h_in * 72, 2)
    objs = ["<< /Type /Catalog /Pages 2 0 R >>", None]
    kids = []
    for i in range(pages):
        num = 3 + i
        kids.append(f"{num} 0 R")
        objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w} {h}] >>")
    objs[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {pages} >>"
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n{body}\nendobj\n".encode()
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    out += b"".join(f"{o:010d} 00000 n \n".encode() for o in offsets)
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


def pagecount() -> None:
    put("kdp-pagecount", "pass", "interior_6x9_bleed_120p.pdf", pdf(120, 6.125, 9.25), {"trim": "6x9", "claimed": 120})
    put("kdp-pagecount", "pass", "hardcover_6x9_80p.pdf", pdf(80, 6, 9), {"format": "hardcover", "trim": "6x9"})
    put("kdp-pagecount", "fail", "paperback_too_few_20p.pdf", pdf(20, 6, 9), {"trim": "6x9"})
    put("kdp-pagecount", "fail", "wrong_trim_letter_size.pdf", pdf(40, 8.5, 11), {"trim": "6x9"})
    put("kdp-pagecount", "fail", "promises_more_pages.pdf", pdf(60, 6, 9), {"trim": "6x9", "claimed": 100})


# ---------------------------------------------------------------- kdp-cover-safezone
def cover(path: Path, w_in, h_in, dpi, boxes) -> None:
    from PIL import Image, ImageDraw

    im = Image.new("RGB", (round(w_in * dpi), round(h_in * dpi)), (236, 228, 210))
    d = ImageDraw.Draw(im)
    for x0, y0, x1, y1 in boxes:  # inches from the top-left corner of the file
        d.rectangle([round(x0 * dpi), round(y0 * dpi), round(x1 * dpi) - 1, round(y1 * dpi) - 1], fill=(40, 52, 90))
    im.save(path, dpi=(dpi, dpi), optimize=True)


def text_line(x0, y0, x1, size):
    """Blocks shaped like a line of letters from x0 to x1 (inches), `size` inches high."""
    out, x = [], x0
    while x + size * 0.7 <= x1 + 1e-9:
        out.append((x, y0, x + size * 0.7, y0 + size))
        x += size
    return out


def covers() -> None:
    dpi = 60
    # Paperback 6 x 9, 120 pages on white paper: spine 0.27 in, file 12.52 x 9.25 in.
    spine = 0.27
    w, h = 2 * 6 + spine + 0.25, 9.25
    front_x = 0.125 + 6 + spine  # back bleed + back panel + spine = left edge of the front panel
    back = text_line(1.0, 1.0, 5.0, 0.3) + [(1.0, 5.0, 5.0, 7.0)]
    title_ok = text_line(front_x + 0.8, 1.0, front_x + 5.2, 0.5)
    title_near_edge = text_line(w - 0.15 - 0.35 - 7 * 0.5, 1.0, w - 0.15, 0.5)  # last letter ends 0.15 in from the edge
    picture = [(front_x + 1.0, 3.0, front_x + 5.0, 7.5)]
    args = {"trim": "6x9", "pages": 120}
    cover(put("kdp-cover-safezone", "pass", "paperback_6x9.png", args=args), w, h, dpi, back + title_ok + picture)
    cover(put("kdp-cover-safezone", "warn", "paperback_title_near_edge.png", args=args), w, h, dpi,
          back + title_near_edge + picture)
    # Saved without bleed: 9.0 in high instead of 9.25.
    cover(put("kdp-cover-safezone", "fail", "paperback_no_bleed.png", args=args), w - 0.25, 9.0, dpi,
          back + title_ok)
    # 60 pages: spine 0.135 in, too thin for spine text under the 79-page rule.
    thin = round(60 * 0.002252, 4)
    tw = 2 * 6 + thin + 0.25
    spine_text = [(6.125 + thin / 2 - 0.05, 2.0 + i * 0.35, 6.125 + thin / 2 + 0.05, 2.25 + i * 0.35) for i in range(6)]
    cover(put("kdp-cover-safezone", "fail", "paperback_spine_text_60_pages.png", args={"trim": "6x9", "pages": 60}),
          tw, h, dpi, back + spine_text)
    # Hardcover 6 x 9 with a 0.6 in spine: text 0.5 in from the outer file edge is fine on a paperback
    # but inside the 0.716 in hardcover wrap zone.
    hs = 0.6
    panel = (14.176 - hs) / 2
    hw, hh = 2 * panel + hs, 10.417
    fx = panel + hs
    hc_ok = [(1.2, 1.2, 5.5, 3.0), (fx + 0.9, 1.2, fx + 5.6, 4.0)]
    hc_bad = [(1.2, 1.2, 5.5, 3.0), (fx + 0.9, 1.2, hw - 0.5, 4.0)]
    hargs = {"format": "hardcover", "trim": "6x9", "spine": hs}
    cover(put("kdp-cover-safezone", "pass", "hardcover_6x9.png", args=hargs), hw, hh, dpi, hc_ok)
    cover(put("kdp-cover-safezone", "fail", "hardcover_text_in_wrap.png", args=hargs), hw, hh, dpi, hc_bad)
    # 0.68 in: outside the help page's 0.635 in, inside the 0.716 in a KDP review cited.
    hc_between = [(1.2, 1.2, 5.5, 3.0), (fx + 0.9, 1.2, hw - 0.68, 4.0)]
    cover(put("kdp-cover-safezone", "warn", "hardcover_between_page_and_review_limit.png", args=hargs), hw, hh, dpi,
          hc_between)


# ---------------------------------------------------------------- epub
FIXED_TIME = (2026, 1, 1, 0, 0, 0)  # fixed ZIP timestamps keep the EPUB fixtures byte-identical
CONTAINER = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
"""
OPF = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:4f1c2a9e-0000-4000-8000-000000000001</dc:identifier>
    {title}
    <dc:language>en</dc:language>
    <dc:creator>Sample Author</dc:creator>
    <meta property="dcterms:modified">2026-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="ch1" href="{chapter}" media-type="application/xhtml+xml"/>
  </manifest>
  <spine><itemref idref="ch1"/></spine>
</package>
"""
NAV = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>Contents</title></head>
<body><nav epub:type="toc"><ol><li><a href="ch1.xhtml">Chapter 1</a></li></ol></nav></body></html>
"""
CHAPTER = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml"><head><title>Chapter 1</title></head>
<body><h1>Chapter 1</h1><p>A short sample chapter used as a test fixture.</p></body></html>
"""


def epub(path: Path, mimetype_stored=True, title=True, chapter_href="ch1.xhtml", broken_xhtml=False) -> None:
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", FIXED_TIME), "application/epub+zip",
                   compress_type=zipfile.ZIP_STORED if mimetype_stored else zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("META-INF/container.xml", FIXED_TIME), CONTAINER, compress_type=zipfile.ZIP_DEFLATED)
        opf = OPF.format(title="<dc:title>Sample Book</dc:title>" if title else "", chapter=chapter_href)
        z.writestr(zipfile.ZipInfo("OEBPS/content.opf", FIXED_TIME), opf, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("OEBPS/nav.xhtml", FIXED_TIME), NAV, compress_type=zipfile.ZIP_DEFLATED)
        body = CHAPTER.replace("</p>", "") if broken_xhtml else CHAPTER
        z.writestr(zipfile.ZipInfo("OEBPS/ch1.xhtml", FIXED_TIME), body, compress_type=zipfile.ZIP_DEFLATED)


def epubs() -> None:
    epub(put("epub", "pass", "minimal_epub3.epub", args={"author": "Sample Author"}))
    epub(put("epub", "fail", "mimetype_compressed.epub"), mimetype_stored=False)
    epub(put("epub", "fail", "no_title_missing_chapter.epub"), title=False, chapter_href="chapter-one.xhtml")
    epub(put("epub", "fail", "broken_xhtml.epub"), broken_xhtml=True)
    epub(put("epub", "fail", "author_mismatch.epub", args={"author": "Another Name"}))


# ---------------------------------------------------------------- media gates (ffmpeg)
def ff(path: Path, *args: str) -> None:
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args, str(path)]
    subprocess.run(cmd, check=True)


def media() -> None:
    sr = "8000"
    syll = "0.4*sin(2*PI*220*t)*gt(sin(2*PI*2*t),-0.2)"  # bursts with 0.2 s pauses, like speech
    ff(put("dead-air", "pass", "short_pauses.flac"), "-f", "lavfi", "-i", f"aevalsrc='{syll}':s={sr}:d=4", "-c:a", "flac")
    ff(put("dead-air", "fail", "gap_2_5s.flac"), "-f", "lavfi", "-i",
       f"aevalsrc='if(between(t,1,3.5),0,{syll})':s={sr}:d=4.5", "-c:a", "flac")
    ff(put("dead-air", "fail", "silent_start_1_5s.flac"), "-f", "lavfi", "-i",
       f"aevalsrc='if(lt(t,1.5),0,{syll})':s={sr}:d=3.5", "-c:a", "flac")

    # 1 kHz sine: about -3 LUFS at full scale, so amplitude 0.28 lands near -14 LUFS.
    ff(put("loudness", "pass", "tone_minus14_lufs.flac"), "-f", "lavfi", "-i", f"aevalsrc='0.28*sin(2*PI*1000*t)':s={sr}:d=4",
       "-c:a", "flac")
    ff(put("loudness", "pass", "tone_minus16_lufs_podcast.flac", args={"profile": "podcast"}), "-f", "lavfi", "-i",
       f"aevalsrc='0.223*sin(2*PI*1000*t)':s={sr}:d=4", "-c:a", "flac")
    ff(put("loudness", "fail", "too_quiet.flac"), "-f", "lavfi", "-i", f"aevalsrc='0.02*sin(2*PI*1000*t)':s={sr}:d=4",
       "-c:a", "flac")
    ff(put("loudness", "fail", "too_loud_for_podcast.flac", args={"profile": "podcast"}), "-f", "lavfi", "-i",
       f"aevalsrc='0.9*sin(2*PI*1000*t)':s={sr}:d=4", "-c:a", "flac")

    ff(put("tail", "pass", "fade_out.flac"), "-f", "lavfi", "-i", f"aevalsrc='0.4*sin(2*PI*330*t)':s={sr}:d=3",
       "-af", "afade=t=out:st=2.4:d=0.4", "-c:a", "flac")
    ff(put("tail", "fail", "cut_mid_note.flac"), "-f", "lavfi", "-i", f"aevalsrc='0.4*sin(2*PI*330*t)':s={sr}:d=3",
       "-c:a", "flac")

    vid = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "35", "-preset", "veryslow", "-an"]
    ff(put("freeze", "pass", "moving_test_pattern.mp4"), "-f", "lavfi", "-i", "testsrc2=s=64x64:r=10:d=4", *vid)
    ff(put("freeze", "fail", "still_frame_4s.mp4"), "-f", "lavfi", "-i", "color=c=gray:s=64x64:r=10:d=4", *vid)


def subtitles():
    for ext in ("srt", "vtt"):
        cues = []
        for i in range(3):
            timing = f"00:00:0{i}.000 --> 00:00:0{i+1}.000"
            if ext == "srt":
                timing = f"{i+1}\n" + timing.replace(".", ",")
            cues.append(timing + "\nCaption")
        body = "\n\n".join(cues) + "\n"
        if ext == "vtt":
            put("subtitles", "fail", "missing_header.vtt", body)
            body = "WEBVTT\n\n" + body
        else:
            put("subtitles", "fail", "overlap.srt", body.replace("01,000 -->", "00,500 -->"),
                args={"overlaps": "reject"})
        put("subtitles", "pass", "three." + ext, body)
    put("subtitles", "pass", "layered.vtt", "WEBVTT\n\n00:00.000 --> 00:02.000\nA\n\n00:01.000 --> 00:03.000\nB\n")
    put("subtitles", "warn", "long_line.vtt", "WEBVTT\n\n00:00.000 --> 00:02.000\nCaption\n",
        args={"max_line_length": 5})
    put("subtitles", "fail", "reversed.vtt", "WEBVTT\n\n00:02.000 --> 00:01.500\nText\n")


GROUPS = {"subtitles": subtitles, "metadata": metadata, "pagecount": pagecount, "covers": covers, "epub": epubs, "media": media}

if __name__ == "__main__":
    chosen = sys.argv[1:] or list(GROUPS)
    unknown = [g for g in chosen if g not in GROUPS]
    if unknown:
        sys.exit(f"unknown group(s) {unknown}; choose from {list(GROUPS)}")
    for name in chosen:
        GROUPS[name]()
    print(f"regenerated: {', '.join(chosen)} (files this script writes are overwritten, others are left alone)")
