# Marathi IPA Research Starter Dataset — add-on for IPA Atlas

**Version:** 1.0, 16 October 2026 | **Status:** source-extracted, not yet expert-verified

This bundle provides **187 pronunciation records / 152 distinct Marathi spellings**:
162 broad and 25 narrow readings, selected *verbatim at segment level* from the `CUNY-CL/wikipron` `mar_deva_broad.tsv` and `mar_deva_narrow.tsv` research datasets. Source blob SHA-1 values are in the CSV and `data/source_manifest.json`.

## What the evidence supports
- Marathi Devanagari spelling and IPA strings are **source-based WikiPron/Wiktionary extractions** (NOT individually measured recordings or an academically refereed pronunciations for each word).
- These specific forms have **unknown speaker, accent, dialect, and recording context** unless otherwise independently documented. `dialect=unspecified` therefore means exactly that; do **not** report them as "Standard Marathi" speaker productions.
- Broad and narrow source representations can differ: e.g., `पाणी /paɳi/` versus `[paɳiː]`; preserve both and distinguish `/ /` from `[ ]`. Syllable separators removed by WikiPron should not be inferred from the original gap-separated source data.
- The `meaning_en` column is an *editorial convenience*, NOT a verified WikiPron field. Glosses may be ambiguous or incomplete. Every such entry has `meaning_provenance=editorial_not_cross_checked`.
- No audio is distributed. No speaker has been sampled. The bundle is **not** a validated Marathi phonetic corpus.

## Installation into your existing GitHub repo

The target is https://github.com/nikhilmugal21/ipa-atlas.

1. Unzip this add-on. In your local **IPA Atlas repository**, copy the `data/`, `ipa_atlas/`, `pages/`, and `scripts/` folders **into the matching folders**, merging rather than replacing the original folders. (For `data/`, place `marathi_examples.csv`; the `source_*_seed.tsv` files are optional reproducibility artefacts.) Do not delete any old files.
2. Copy `MARATHI_SOURCES_AND_REVIEW.md` to the repo root.
3. From the IPA Atlas repository root, run `python scripts/patch_ipa_atlas.py`. This safely backs up and patches your existing `ipa_atlas/catalog.py` and `ipa_atlas/main.py` only if their expected signatures match.
4. Run `python -m pytest -q` (if `pytest` installed), followed by `streamlit run streamlit_app.py`.
5. Commit the added files and the two patched `.py` files to GitHub (don't commit `.before_marathi.bak` backups). Streamlit should redeploy. The **Marathi Pronunciation Lexicon** page appears in Streamlit's navigation, and source-derived Marathi examples also appear when selecting a phone in the existing explorer.
6. FastAPI adds `GET /v1/marathi/summary`, `GET /v1/marathi/words?q=पाणी`, `GET /v1/marathi/words?phone=ɳ&level=broad`, and `GET /v1/marathi/phone/ɳ` when run under FastAPI; Streamlit hosting itself does **not** publicly expose REST routes.

If you prefer no editing of existing `.py` files, you can copy just `data/marathi_examples.csv`, `ipa_atlas/marathi_lexicon.py`, and `pages/1_Marathi_Pronunciation_Lexicon.py` to gain the separate Streamlit page. The explorer and REST backend will remain unchanged.

## Make the full (thousands-of-entries) dataset on your Mac

Using the installed project root, with Python 3.11+ and an internet connection:

```bash
python scripts/download_full_wikipron.py
python scripts/build_marathi_dataset.py \
  --broad data/raw/mar_deva_broad.tsv \
  --narrow data/raw/mar_deva_narrow.tsv
```

These scripts require only the Python standard library. The downloader validates the exact Git blob IDs used during compilation, so a changed upstream file triggers a review instead of silently replacing the data. Building with the complete TSVs will replace `data/marathi_examples.csv`, while keeping every source pronunciation variant.

## Main field glossary

| Field | Meaning |
|---|---|
| `orthography` | Marathi Devanagari headword/form |
| `ipa` | Source-reconstructed IPA, `/.../` for broad or `[...]` for narrow |
| `source_segmented_ipa` | Original source field preserved, e.g. `p a ɳ iː` |
| `ipa_tokens` | Source token boundaries separated by `|` for precise phone searching |
| `transcription_level` | Source export (`broad` or `narrow`) |
| `source_blob_sha` | Verified Git blob ID of upstream TSV file |
| `wiktionary_entry_url` | Link to underlying community-sourced dictionary entry |
| `dialect` | `unspecified` pending review |
| `meaning_en` | Editorial approximate English gloss; NOT verified by source |
| `verification_status` | `source_extracted_not_expert_reviewed` |
| `speaker_audio_url` | Blank: no recording is available in this dataset |

## Why not merge phoneme inventories with examples?

PHOIBLE documents **phonemic inventories** reported by studies. WikiPron supplies **lexical transcriptions** mined from Wiktionary. They are not interchangeable evidence. A published PHOIBLE phoneme doesn't automatically verify a phone in one lexical item. Keep the two parts of IPA Atlas separate, linked only by explicit IPA-symbol searches.

## Research citation and reuse

**Lee, Jackson L. et al. (2020).** “Massively Multilingual Pronunciation Modeling with WikiPron.” *Proceedings of LREC 2020*, 4223–4228. https://aclanthology.org/2020.lrec-1.521/.

**Primary community content:** English Wiktionary pronunciation entries; https://en.wiktionary.org/wiki/Wiktionary:Copyrights. The source WikiPron software is Apache-2.0, but **Wiktionary-derived data has separate share-alike licensing** (typically CC BY-SA 3.0). Attribution, share-alike and edition/history requirements should be maintained if you publish these records. Check the exact upstream licensing before public redistribution; do not assume your existing repository's MIT licence covers the data. See `MARATHI_SOURCES_AND_REVIEW.md`.

C-DAC also documents an IPA/Pronunciation Lexicon initiative involving Marathi and instrumental verification (EPG/EGG); we did **not** download or use its lexicon and do not claim to have verified WikiPron entries with that project. https://cdac.gov.in/index.aspx?id=mc_s_IPA_PLS.
