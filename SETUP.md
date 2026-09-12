# Setup

## 1. Create the special repo (one-time)
```
gh repo create swagatgharat --public --clone
cd swagatgharat
# copy everything from this folder in here
```
Its `README.md` renders at the top of your GitHub profile automatically —
that's the only thing special about a repo named exactly like your username.

## 2. Generate your real ASCII portrait (local, one-time)
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements-portrait.txt
python scripts/prep_photo.py your-photo.jpg
python scripts/make_ascii_svg.py
```
This downloads a small (~4MB) background-removal model on first run.
Re-run these two commands only when you change your photo — commit the
resulting `avi-ascii.svg` (it replaces the placeholder already in this repo).

## 3. Generate the heatmap once locally, then let the cron take over
```
pip install -r scripts/requirements-daily.txt
GH_USERNAME=swagatgharat python scripts/fetch_contributions.py
python scripts/render_heatmap_svg.py
```
`contrib-heatmap.svg` and `info-card.svg` in this folder were already
generated once with your real data — this step is only needed if you want
to regenerate before pushing, or after editing `make_info_card.py`'s ROWS.

## 4. Push
```
git add -A
git commit -m "profile: animated terminal README"
git push
```
The workflow in `.github/workflows/update-profile-art.yml` then re-scrapes
and re-renders the heatmap daily and commits it — no token needed, since it
reads the same public HTML endpoint the profile page itself uses.

## Editing your info card
Edit the `ROWS` list at the top of `scripts/make_info_card.py`, then run
`python scripts/make_info_card.py` and commit the result. It's static
content — not part of the daily automation.

## If GitHub changes its contribution-calendar markup
`fetch_contributions.py` will fail loudly in the Action logs but won't
overwrite your existing `data/contributions.json` (see the try/except in
`main()`) — the README keeps showing the last good heatmap until you fix
the selectors in `parse_days()`.
