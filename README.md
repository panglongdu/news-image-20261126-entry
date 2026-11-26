# The World in One Day — 26 November 2026

Entry for the make.fun bounty
[Sum up 26 November's world news in one image](https://make.fun/bounty/news-image-20261126).

`build_image.py` draws the front page from scratch with Pillow:
a masthead dated Thursday 26 November 2026, a hero panel on
Shenzhou-24 carrying Muhammad Zeeshan Ali — the first Pakistani in
orbit and the first foreign astronaut aboard China's Tiangong
station — a markets panel, a four-cell data strip (Cairo tanker
fire, Bangladesh wage rise, Colombia's ten years of peace,
Venezuela's debt), six short stories and a ticker.

`main.py` copies the built `entry.png` to the grader's output
directory. Running `build_image.py` twice writes identical bytes.

## Run

```sh
python3 build_image.py
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Licence

MIT — see `LICENSE`.
