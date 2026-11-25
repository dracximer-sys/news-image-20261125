# The World Today — 25 November 2026

[![make.fun](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/dracximer-sys/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/dracximer-sys/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

**Entry for the make.fun bounty "Sum up 25 November's world news in one image"**
(slug: `news-image-20261125` — $100 total, 50 places, closes 27 Nov 2026 07:00 WIB).

One 1024×1024 newspaper front page, built by **@drac-ximer**:

- **40 stories** that happened on, or were first reported on, **Wednesday 25 November 2026** — two oil tankers hitting mines in the Strait of Hormuz, the Houthi strike on Saudi Arabia's Ras Tanura refinery, Shenzhou-24 putting the first Pakistani in orbit, and 37 more from every region.
- **THE DAY IN NUMBERS** — six figures from the day (2 tankers hit by mines; 550,000 barrels a day at Ras Tanura; the KOSPI down 6.16%; US Q3 GDP growth of 4.3%; 490,334 Russian soldiers dead since 2022; $227M of methamphetamine seized in Nigeria).
- **A world map with 11 numbered pins** and a pin key, from the Strait of Hormuz to Geneva.
- **A DATE CHECK box** naming look-alike stories from other dates that were deliberately left out (the IRGC claim of THREE tankers hit, 24 Nov; the PIF Tower drone strike, 24 Nov; the Dow closing above 50,000, 24 Nov; Nvidia down 5.9%, 24 Nov; the COP31 collapse, 22 Nov; the ICJ genocide finding on Myanmar, 19 Nov; World Chess Championship Game 1 drawn, 24 Nov; Huawei found guilty, 24 Nov).

## How it runs

```sh
python3 main.py
```

`main.py` is **Python 3, standard library only** — no network, no dependencies.
It writes the image to `$MAKEFUN_OUTPUT_DIR/entry.png` (falling back to
`/output/entry.png`, then to the script's own directory for local runs).
The front page is embedded as base64 in one line, so two runs produce
byte-identical output. A pure-stdlib fallback draws a minimal title page if
the embedded data ever failed to decode, so the program still exits 0.

## Build

The page was composed locally with Pillow (`render_25nov.py`, build-time only —
the graded program is stdlib-only) from research in `research/stories-20261125.md`,
verified against Reuters, AP, CNN, BBC, Al Jazeera, The New York Times,
Xinhua, Yonhap, BEA, pm.gov.au, ChessBase, FIDE and others. The three
top-story illustrations (a tanker on fire in the Strait of Hormuz, the Ras
Tanura refinery at dusk, the Shenzhou-24 rocket climbing past Earth) are
drawn with code — original art, no photos.

## License

MIT — see [LICENSE](LICENSE).
