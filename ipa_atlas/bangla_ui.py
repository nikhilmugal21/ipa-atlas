"""Streamlit section for WikiPron-derived Bangla lexical pronunciations."""
from __future__ import annotations

import csv
import io
import streamlit as st
from .bangla_lexicon import records, stats, search


def render_bangla_dataset() -> None:
    st.subheader("Bangla · pronunciation dataset")
    info = stats()
    if not info["complete"]:
        st.warning("One or more source files are missing from data/bangla_wikipron/.")
    if not info["records"]:
        st.error("No Bangla pronunciation data available.")
        return

    col1, col2 = st.columns(2)
    col1.metric("Pronunciation records", f'{info["records"]:,}')
    col2.metric("Distinct spellings", f'{info["unique_spellings"]:,}')
    st.caption(
        "Extracted from WikiPron/Wiktionary, NOT independently speaker-verified. "
        "Dhaka and Rarh designate WikiPron dialect-filtered source groups; "
        "unlabeled Wiktionary pronunciations may occur in both. "
        "WikiPron supplies no English translations."
    )

    with st.expander("Research provenance and coverage"):
        st.dataframe(info["by_source"], hide_index=True, use_container_width=True)
        st.markdown(
            "Source: [WikiPron](https://github.com/CUNY-CL/wikipron), "
            "Lee et al. (2020), from [Wiktionary](https://en.wiktionary.org/). "
            "See data/bangla_wikipron/ATTRIBUTION.md for licences and source blob IDs."
        )

    query = st.text_input("Search Bangla spelling or IPA", key="bangla-query")
    col1, col2, col3 = st.columns(3)
    with col1:
        dialect = st.selectbox("Dialect filter", ["Both", "Dhaka", "Rarh"], key="bangla-dialect")
    with col2:
        level = st.selectbox("Transcription", ["Both", "broad", "narrow"], key="bangla-level")
    with col3:
        phones = sorted({token for record in records() for token in record["ipa_tokens"]})
        phone = st.selectbox("IPA segment (exact match)", ["All", *phones], key="bangla-phone")

    matches = search(
        q=query,
        dialect=None if dialect == "Both" else dialect,
        level=None if level == "Both" else level,
        phone=None if phone == "All" else phone,
    )
    st.caption(f'{len(matches):,} matching source records. Multiple pronunciations for a spelling are preserved.')

    first, second = st.columns(2)
    with first:
        page_size = st.selectbox("Rows per page", [25, 50, 100, 250], index=1, key="bangla-page-size")
    num_pages = max(1, (len(matches) + page_size - 1) // page_size)
    with second:
        page = int(st.number_input("Page", min_value=1, max_value=num_pages, step=1, key="bangla-page"))
    current = matches[(page-1)*page_size:page*page_size]

    st.dataframe(
        [{
            "Word": x["orthography"],
            "IPA": x["ipa"],
            "Dialect filter": x["dialect_filter"],
            "Transcription": x["transcription_level"],
            "Source": x["wiktionary_entry_url"],
        } for x in current],
        hide_index=True, use_container_width=True,
    )
    if current:
        st.markdown("#### Source details")
        choices = {x["id"]: x for x in current}
        selected_id = st.selectbox(
            "Select entry",
            list(choices),
            format_func=lambda key: (
                f'{choices[key]["orthography"]} · {choices[key]["ipa"]} · '
                f'{choices[key]["dialect_filter"]}/{choices[key]["transcription_level"]}'
            ),
            key="bangla-selected-entry",
        )
        row = choices[selected_id]
        st.markdown(f'**{row["orthography"]}** — {row["ipa"]}')
        st.caption(f'Original segmented IPA: {row["source_segmented_ipa"]}')
        st.markdown(
            f'[Wiktionary entry]({row["wiktionary_entry_url"]}) · '
            f'[WikiPron source file]({row["source_file_url"]})'
        )
        st.caption("Provenance: source extraction; no speaker-confirmed audio or English definition.")

    if matches:
        fields = [
            "orthography", "ipa", "dialect_filter", "transcription_level",
            "source_segmented_ipa", "source_file", "source_blob_sha",
            "wiktionary_entry_url", "verification_status",
        ]
        f = io.StringIO()
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: item.get(key, "") for key in fields} for item in matches)
        st.download_button(
            "Export matching entries (CSV)", f.getvalue().encode("utf-8-sig"),
            file_name="bangla_ipa_filtered.csv", mime="text/csv", key="bangla-export",
        )
