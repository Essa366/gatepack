# Good first issues

Fifteen gates that do not exist yet. Each one is an open GitHub issue labelled `good first issue`
([all of them](https://github.com/Essa366/gatepack/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)),
with the rule as read on 2026-11-20, suggested PASS and FAIL fixtures and the acceptance criteria.
Comment on the issue to claim one, then follow [adding-a-gate.md](adding-a-gate.md).

For every gate: read the linked page first and copy the current numbers from it into the module and the
docs page. Platforms change their limits, so the page, not this list, is the source.

| Issue | Gate id | What it checks | Where the rule is | Size |
|---|---|---|---|---|
| [#1](https://github.com/Essa366/gatepack/issues/1) | `youtube-thumbnail` | thumbnail resolution, aspect ratio, file size and format | YouTube Help, "Add video thumbnails": https://support.google.com/youtube/answer/72431 | S |
| [#2](https://github.com/Essa366/gatepack/issues/2) | `pinterest-pin` | pin image aspect ratio and minimum size | Pinterest Business, creative specs: https://business.pinterest.com/creative-best-practices/ | S |
| [#3](https://github.com/Essa366/gatepack/issues/3) | `etsy-listing-photo` | listing photo minimum size and recommended ratio | Etsy Help, "Requirements and Best Practices for Images in Your Etsy Shop": https://help.etsy.com/hc/en-us/articles/115015663347 | S |
| [#4](https://github.com/Essa366/gatepack/issues/4) | `kdp-ebook-cover` | eBook cover pixel size, aspect ratio, file size | KDP, "Cover Image Guidelines for Kindle eBooks": https://kdp.amazon.com/en_US/help/topic/G6GTK3T3NUHKLEFX | S |
| [#5](https://github.com/Essa366/gatepack/issues/5) | `app-store-screenshot` | screenshot sizes per device class | Apple, screenshot specifications: https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications | M |
| [#6](https://github.com/Essa366/gatepack/issues/6) | `play-store-graphics` | feature graphic and screenshot sizes | Play Console Help, "Add preview assets to showcase your app": https://support.google.com/googleplay/android-developer/answer/9866151 | M |
| [#7](https://github.com/Essa366/gatepack/issues/7) | `og-image` | Open Graph image present in an HTML file, size and ratio of the referenced image | The Open Graph protocol: https://ogp.me/ | M |
| [#8](https://github.com/Essa366/gatepack/issues/8) | `black-frames` | black segments at the start or inside a video | heuristic, measured with FFmpeg blackdetect: https://ffmpeg.org/ffmpeg-filters.html#blackdetect_002c-blackdetect_005fvulkan | S |
| [#9](https://github.com/Essa366/gatepack/issues/9) | `audio-clipping` | samples at or near full scale (digital clipping) | heuristic, measured with FFmpeg astats: https://ffmpeg.org/ffmpeg-filters.html#astats-1 | S |
| [#10](https://github.com/Essa366/gatepack/issues/10) | `video-dimensions` | width, height and aspect ratio against a target you pass (e.g. vertical 1080 x 1920) | YouTube Help, "Get started creating YouTube Shorts" (vertical video, resolution cap): https://support.google.com/youtube/answer/10059070 | S |
| [#11](https://github.com/Essa366/gatepack/issues/11) | `subtitles` | SRT/WebVTT files: timestamps in order, no overlaps, line length | W3C WebVTT: https://www.w3.org/TR/webvtt1/ | M |
| [#12](https://github.com/Essa366/gatepack/issues/12) | `acx-audiobook` | audiobook chapter files: RMS level, peak level, noise floor, room tone at start and end | ACX audio submission requirements: https://www.acx.com/help/article/acx-audio-submission-requirements | M |
| [#13](https://github.com/Essa366/gatepack/issues/13) | `kdp-interior-margins` | text inside the minimum gutter and outside margins for the page count | KDP, "Set Trim Size, Bleed, and Margins": https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6 | L |
| [#14](https://github.com/Essa366/gatepack/issues/14) | `ingramspark-cover` | cover size, bleed and safe area for IngramSpark print books | IngramSpark File Creation Guide: https://www.ingramspark.com/hubfs/downloads/file-creation-guide.pdf | M |
| [#15](https://github.com/Essa366/gatepack/issues/15) | `print-image-resolution` | images embedded in a print PDF below the resolution the printer asks for | KDP, "Fix Paperback and Hardcover Formatting Issues", image resolution section: https://kdp.amazon.com/en_US/help/topic/G201834260 | M |

Size: S = one evening, M = a weekend, L = needs PDF text extraction or more design.

## Links checked

All fifteen links loaded on 2026-11-20. Two had moved and are updated above: the Apple screenshot page
(now under `reference/app-information/`) and the ACX requirements page (now under `help/article/`).
