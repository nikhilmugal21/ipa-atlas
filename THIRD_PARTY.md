# Source attribution and reuse policy

This app **does not include copyrighted IPA chart artwork or official audio recordings**. The author-created descriptions are based on standard phonetic classifications and refer to the chart as the authority on its symbols.

| Resource | URL | Used in this release | Caution |
|---|---|---|---|
| Official IPA chart | https://www.internationalphoneticassociation.org/content/ipa-chart | Reference for 107 core symbol shapes, chart classes, diacritics and prosody; no graphics distributed | Official IPA Kiel chart graphics are CC BY-SA 4.0 with attribution and sharealike requirements |
| Handbook of the IPA language illustration audio | https://www.internationalphoneticassociation.org/node/125 | Source link only | **Do not redistribute recordings** without permission; educational personal download permissions are not product redistribution permissions |
| CMU Pronouncing Dictionary | https://github.com/cmusphinx/cmudict | Optional independently installed US English lexical pronunciation resource | Respect its licence; ARPAbet-to-IPA mapping is an approximation |
| `cmudict` Python package | https://pypi.org/project/cmudict/ | Optional separately installed wrapper | The Python wrapper itself declares GPL-3.0-or-later; not bundled here |
| PHOIBLE | https://phoible.org/download | Optional user-imported CSV phoneme inventories | **Licensing varies by source/distribution**; official PHOIBLE 2.0 download says CC BY-SA 3.0; current `phoible/dev` data tree states CC BY 4.0. Check the exact version you download. Keep source & inventory IDs |
| PanPhon | https://github.com/dmort27/panphon | Integration candidate, not a dependency | Confirm licence when deciding to integrate; cannot replace phonetic descriptions with feature vectors automatically |
| Bangla WikiPron pronunciation TSVs (from English Wiktionary) | https://github.com/CUNY-CL/wikipron/tree/master/data/scrape/tsv | Four source files: Dhaka/Rarh dialect filters × broad/narrow; displayed in Streamlit and REST endpoints | Underlying Wiktionary material has CC BY-SA 4.0 / GFDL licensing distinct from WikiPron Apache-2.0 software. Separate data notice and original blob SHA IDs are at `data/bangla_wikipron/ATTRIBUTION.md`. Not speaker verified. |
| Wiktionary | https://www.wiktionary.org/ | External human reference and source of the separately attributed WikiPron Bangla data | Attributions and content licences matter. Pronunciations vary by region |

Read these pages directly for up-to-date terms. No dependency on a proprietary API or paid account is necessary for core functions.
