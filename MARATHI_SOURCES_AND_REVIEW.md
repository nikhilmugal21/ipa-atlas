# Sources, scientific limitations, and phonetic review protocol

## Sources actually used to construct this starter dataset

1. **WikiPron Marathi data**: `mar_deva_broad.tsv` and `mar_deva_narrow.tsv` in https://github.com/CUNY-CL/wikipron/tree/master/data/scrape/tsv, upstream Git blob IDs in `source_manifest.json` and per-record CSV. (These are word/pronunciation pairs extracted from Wiktionary.)
2. **En-Wiktionary**: lexical-source URLs are included per record. This is collaboratively edited lexicographic content, **not** laboratory phonetic measurement.
3. **WikiPron research citation**: Jackson L. Lee et al. (2020), *Massively Multilingual Pronunciation Modeling with WikiPron*, LREC pp. 4223–4228, https://aclanthology.org/2020.lrec-1.521/.
4. **Official IPA Chart**: https://www.internationalphoneticassociation.org/content/ipa-chart used for descriptive convention only. No IPA art or audio redistributed.

### Contextual references not used as transcription sources
- C-DAC's IPA-PLS initiative includes Marathi and mentions EPG/EGG and lexicon work: https://cdac.gov.in/index.aspx?id=mc_s_IPA_PLS. Dataset not publicly verified as downloadable here; no assumption of reuse rights.
- PHOIBLE: https://phoible.org/ contains published language-level phoneme inventories, NOT word-level transcriptions and must not be presented as a pronunciation source.

## Required quality assurance before saying "verified Marathi phonetic dataset"

1. Fix a specific speaker variety and location (e.g. self-identified Mumbai/Pune/Nagpur variety), speaking style and recording protocol; **do not infer dialect from spelling**.
2. Verify word senses and editorial English glosses against independently cited dictionaries. Note ambiguities such as `नाव` (name/boat).
3. In a consent-based elicitation, record 2–3 native speakers per variety (more for quantitative generalisations), using a consistent microphone, audio format and prompt set. Keep identifying metadata private unless participants agree to sharing.
4. Use Praat to inspect aspiration, closure, VOT, formants, nasalization and segments. Keep **phonemic** and **phonetic** tiers separate. Note any discrepancy between source WikiPron IPA and speaker realizations.
5. Have a second trained transcriber check a subset; store agreement and adjudicated labels. Mark observations `expert_reviewed` only when actually reviewed.
6. Keep a stable ID linking orthography, IPA, source, dialect, token segmentation, reviewer, and optional restricted audio URI. Add citations/page numbers when validating against published phonetic studies.
7. Maintain distinct rows for variants and do not assume a long written vowel is long in phonemic representation. Preserve the WikiPron source's unusual `ɭ̆` (extra-short diacritic) and `t͡ɕ`/`t͡s` distinctions; review them rather than globally rewriting.
8. For public release, include a DATA LICENSE/NOTICE file separating code license from Wiktionary-derived data license. Cite WikiPron and individual entries, and keep links to upstream attribution/history.

## Future dataset schema suggestions

Add `audio_uri_private`, `consent_scope`, `speaker_pseudonym`, `region`, `age_group_optional`, `register`, `phonetic_tier`, `acoustic_measurements`, `elicitation_context`, `recording_timestamp`, `original_source_page`, `reviewer_confidence`, and `quality_flags` when speaker data are collected and access controls are implemented.
