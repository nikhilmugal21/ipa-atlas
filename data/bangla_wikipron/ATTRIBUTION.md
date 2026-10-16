# Bangla pronunciation data — provenance, research caveats, and licensing

This folder contains four **unmodified** UTF-8, tab-separated pronunciation files obtained from the CUNY-CL WikiPron project on 2026-10-16. Data originated from community-edited English Wiktionary. The site displays each lexical entry's original Wiktionary page link; the Python adapter joins the segmented IPA tokens for display, leaving the original files unchanged.

## Dataset coverage

| Source | Rows | Git blob SHA |
|---|---:|---|
| `ben_beng_dhaka_broad.tsv` | 7,277 | `6ab23861f695e9172ae09881265b3523267a8aa5` |
| `ben_beng_dhaka_narrow.tsv` | 6,949 | `e3eb58cc0b2cc3a1acd9ad4f5acc7b6ac352579c` |
| `ben_beng_rarh_broad.tsv` | 7,525 | `53e2dc72b043d2c6960813352587944def88d56a` |
| `ben_beng_rarh_narrow.tsv` | 7,187 | `37baeb445c7f0bbb59d6a423283171abda706783` |

Total: **28,938 word–pronunciation records** (not 28,938 distinct words). Alternative pronunciations and differences between Dhaka and Rarh source collections are deliberately retained. Original files: https://github.com/CUNY-CL/wikipron/tree/master/data/scrape/tsv

## Research cautions

- **These are source-derived entries, NOT expert-reviewed acoustic transcriptions.** WikiPron was used to scrape community-edited pronunciations on Wiktionary. Dataset quality varies by entry and can contain inconsistent segmentation or sound descriptions.
- The source files use *dialect filters* labelled `Dhaka` and `Rarh`; the WikiPron method may also include entries **without any dialect specification** within either filtered subset. These labels must never be treated as verified speaker provenance.
- Broad transcriptions are shown between /slashes/ and narrow between [brackets] as specified by WikiPron. This does not establish a unique phonemic analysis for either variety.
- A token such as `t͡ʃʰ` is kept as an exact segment sequence from the source. Exact IPA-token search does not infer allophones or remove diacritics.
- WikiPron TSVs do **not** contain translations, definitions, speaker audio, timestamps of original word utterances, confidence scores, or morphological information. **None are fabricated**.
- Use speaker recordings, documented literature and expert review before making substantive phonological claims or treating dialect classification as certain.

## Citation

Lee, Jackson L., Lucas F. E. Ashby, M. Elizabeth Garza, Yeonju Lee-Sikka, Sean Miller, Alan Wong, Arya D. McCarthy, and Kyle Gorman (2020). "Massively multilingual pronunciation mining with WikiPron." *Proceedings of LREC*, 4223–4228. https://aclanthology.org/2020.lrec-1.521/

WikiPron repository: https://github.com/CUNY-CL/wikipron

Wiktionary contributors, source entry pages: https://en.wiktionary.org/

## Licensing and attribution

- The **WikiPron software** is under Apache-2.0, but WikiPron explicitly warns that its Wiktionary-derived `data/` files are subject to **separate Wiktionary licensing**.
- The original text of English Wiktionary entries is made available under **Creative Commons Attribution–ShareAlike 4.0 (CC BY-SA 4.0)** and GFDL terms: https://en.wiktionary.org/wiki/Wiktionary:Copyrights
- This copy of source-derived lexical data is distributed under the applicable **CC BY-SA 4.0** terms, separately from the project's software license. The original WikiPron TSVs are redistributed without modification, and full provenance is listed above.
- Each displayed word has a live Wiktionary entry URL to facilitate contributor attribution and review; Wiktionary revision histories identify contributors. Attribution to WikiPron and citation of the LREC paper are also provided.
- No recordings or images are redistributed, and any future imported external material must be checked under its own licensing terms.

For future research, add a speaker-reviewed dataset in a *separate* file with consent, recording provenance, dialect information and reviewer notes. Do not overwrite these historical source records.
