# Reference — identifiers, people, and things that are not obvious

Facts that are true across volumes and easy to lose, because they live scattered in config files or
nowhere at all. Everything here was verified against the repositories or the live site.

---

## Identifiers

| | |
|---|---|
| Venue | `ncssm-mor` |
| Venue DOI | `10.62329/TJYM8050` |
| Site | <https://morgantonscientific.ncssm.edu> |
| Collections | one per volume, named by year: `2025`, `2026`, `2027` … |
| Article id pattern | `^morganton-<year>-[a-zA-Z0-9_-]{2,15}$` — the suffix is capped at **15 characters** |

The collection name in a volume repository's four workflows must match the `:collection:` used in
[`morsci-website`](https://github.com/ncssm/morsci-website). If they disagree the site's listing
renders empty, with no error on either side.

## Volumes

| Volume | Year | Repository | Issue DOI | Editors-in-Chief |
|---|---|---|---|---|
| 1 | 2024 | — | — | — |
| 2 | 2024–25 | [`morgantonscientific2025`](https://github.com/ncssm/morgantonscientific2025) | `10.62329/dwgm3685` | Armaan Gera, Laira Lee, Mickayla Belus |
| 3 | 2025–26 | [`morgantonscientific2026`](https://github.com/ncssm/morgantonscientific2026) | `10.62329/jnwd8866` | Henry Chen, Clara Lappan, Alex Qu |
| 4 | 2026–27 | [`morgantonscientific2027`](https://github.com/ncssm/morgantonscientific2027) | *to be minted* | *TBD* |

**Issue DOIs are minted by Curvenote, one per volume, and must never be carried over.** Reusing a
previous volume's value files this volume's articles under the wrong issue record. Volume 3 published
as 160 pages on 1 September 2026; its print edition is archived at
[`v3.0`](https://github.com/ncssm/morgantonscientific2026/releases/tag/v3.0).

## People

Curvenote maintain the actions, the templates and the venue. On GitHub: **@fwkoch** and **@rowanc1**.
They have opened PRs directly against these repositories — Volume 3's DOIs and print-PDF scripts came
in that way, as did the website's 2026 listings.

---

## Things that are not obvious from the code

### `frontmatter/` reaches Curvenote, even though no workflow submits it

Reading the four workflows suggests otherwise — they glob only `papers/*` and `essays/*`. But the
frontmatter project **is** in Curvenote: it appears on
<https://morgantonscientific.ncssm.edu/volumes> as "Morganton Scientific - Volume N", credited to the
editors-in-chief, and it serves the **complete** print PDF via the `downloads: Download Full PDF`
declaration in `frontmatter/myst.yml`.

It gets there by another route, most likely a direct submission by Curvenote during DOI setup. So:

- The `volumes` collection is **not** empty, and `/volumes` is **not** broken.
- The full print PDF **is** already served from the site. A separate link to the GitHub release would
  duplicate it.
- Changing anything in `frontmatter/` will **not** be picked up by `submit.yml`, because no path glob
  matches it. Use `resubmit_dispatch.yml`.

### A failing check does not stop publication

`strict` defaults to `false` in the reusable submit workflow, and none of these repositories override
it. Checks run and report, but `publish_dispatch.yml` proceeds regardless. If checks should be a hard
gate, add `strict: true` to both jobs.

### The website deploys with no preview

Pushing to `main` in `morsci-website` makes the site live within minutes — no draft mode, no checks,
nothing equivalent to the `draft` label here. Its README says so, but the habit built in this
repository is the opposite one.

### Publication date is metadata, not a schedule

Nothing fires on the date in `frontmatter/volume.yml`. It is what appears in the Crossref record and
on the articles; publication happens when someone runs `publish_dispatch.yml`.

---

## Open questions for Curvenote

- **What does withdrawal look like after publication**, and what happens to a minted DOI? Not
  answerable from the code, and worth knowing before pressing publish rather than after.
- **How is the `volumes` collection meant to be populated?** It works, but by a route that is not in
  any workflow, so nobody here can reproduce or repair it.
- **Listing cards show the publication date one day early.** Volume 3 is dated 2026-09-01 and the
  article pages render "Sep 1, 2026" correctly, but the cards on the homepage and `/articles` show
  `8/31/2026` — a timezone artifact in the card renderer.
