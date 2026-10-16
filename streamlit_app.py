"""IPA Atlas: Streamlit Community Cloud application.

This UI imports the original IPA Atlas modules directly and does not run a
FastAPI/uvicorn subprocess. Run `streamlit run streamlit_app.py` from repo root.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import streamlit as st

from ipa_atlas.catalog import (
    SOUNDS,
    DIACRITIC_DATA,
    SUPRA_DATA,
    TONES,
    SOURCE,
    EXAMPLES,
    examples_for,
)
from ipa_atlas.analyze import compare, describe_sequence, tokenize
from ipa_atlas.english import lookup_english
from ipa_atlas.inventories import status as inventories_status, list_inventories, inventory_items, attestations

st.set_page_config(page_title="IPA Atlas · Interactive Phonetics", page_icon="🔤", layout="wide")

CATEGORY_NAMES = {
    "pulmonic_consonant": "Pulmonic consonants",
    "nonpulmonic_consonant": "Non-pulmonic consonants",
    "other_consonant": "Other consonants",
    "vowel": "Vowels",
    "composite_consonant": "Common affricates",
}
LANGUAGES = ["Hindi", "Marathi", "Bangla", "Malayalam", "Gujarati", "Tamil", "English"]

# Marathi lexical transcriptions mined from WikiPron/Wiktionary; not speaker-verified.
MARATHI_CSV = Path(__file__).resolve().parent / "data" / "marathi_examples.csv"


@st.cache_data(show_spinner=False)
def marathi_records() -> list[dict[str, str]]:
    if not MARATHI_CSV.is_file():
        return []
    with MARATHI_CSV.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def marathi_phone_examples(symbol: str, limit: int = 8) -> list[dict[str, Any]]:
    rows = [row for row in marathi_records()
            if symbol in row.get("ipa_tokens", "").split("|")]
    rows.sort(key=lambda row: (row["transcription_level"] != "broad",
                               len(row["orthography"]), row["orthography"]))
    return [{
        "language": "Marathi", "word": row["orthography"], "ipa": row["ipa"],
        "meaning": row["meaning_en"], "type": "source_derived_lexical_example",
        "verification": row["verification_status"],
        "notes": f"{row['transcription_level']} · WikiPron/Wiktionary · dialect unspecified",
        "source_url": row["wiktionary_entry_url"],
    } for row in rows[:limit]]


def render_json(data: Any, filename: str) -> None:
    with st.expander("View structured analysis (JSON)"):
        st.json(data)
        st.download_button(
            "Download JSON", data=json.dumps(data, ensure_ascii=False, indent=2),
            file_name=filename, mime="application/json", key=f"json-{filename}"
        )


def display_example(ex: dict[str, Any]) -> None:
    kind = ex.get("type", "")
    title = ex.get("word") or ex.get("ipa") or "Pronunciation exercise"
    label = "Constructed practice sequence" if kind == "constructed_articulatory_drill" else "Illustrative example"
    with st.container(border=True):
        st.markdown(f"**{title}** · `{ex.get('ipa', '')}`")
        st.caption(f"{ex.get('language','Unspecified')} · {label}" + (f" · {ex['meaning']}" if ex.get('meaning') else ""))
        if kind == "constructed_articulatory_drill":
            st.info("This is a practice sequence, **not an attested word**.", icon="ℹ️")
        elif ex.get("verification"):
            st.caption("Pronunciation may vary by speaker, dialect or source; verify before research use.")
        if ex.get("notes"):
            st.caption(ex["notes"])
        if ex.get("source_url"):
            st.markdown(f"[View lexical source]({ex['source_url']})")


def display_description(symbol: str, example_language: str | None = None) -> None:
    try:
        result = describe_sequence(symbol)
    except ValueError as exc:
        st.error(f"Unrecognised IPA symbol or sequence: {exc}")
        return
    st.markdown(f"### {result['symbol']} · {result['name'].capitalize()}")
    st.markdown(result.get("description", "No description recorded."))
    detail1, detail2, detail3, detail4 = st.columns(4)
    for column, heading, value in [
        (detail1, "Place / tongue position", result.get("place") or result.get("backness") or "—"),
        (detail2, "Manner / vowel height", result.get("manner") or result.get("height") or "—"),
        (detail3, "Voicing / rounding", result.get("voicing") or result.get("rounding") or "—"),
        (detail4, "Airstream", result.get("airstream") or "—"),
    ]:
        with column:
            st.caption(heading)
            st.write(str(value).capitalize())

    if result.get("modifiers"):
        st.markdown("**Additional modifications**")
        for modifier in result["modifiers"]:
            st.write(f"- `{modifier['symbol']}` **{modifier['name']}** — {modifier.get('description', '')}")
    if result.get("notes"):
        st.info(result["notes"], icon="ℹ️")

    st.markdown("#### Examples and pronunciation exercises")
    items = examples_for(symbol, example_language)
    if example_language in (None, "Marathi"):
        items = [*items, *marathi_phone_examples(symbol)]
    real = [x for x in items if x["type"] != "constructed_articulatory_drill"]
    drills = [x for x in items if x["type"] == "constructed_articulatory_drill"]
    if not real:
        st.caption("No vetted lexical example is included for this selection. Try another language or an articulatory drill.")
    for example in real + drills:
        display_example(example)
    render_json({**result, "examples": items}, f"ipa-{symbol.encode('utf-8').hex()}.json")


def explorer_page() -> None:
    st.title("IPA Sound Explorer")
    st.write("Search the IPA chart, select a phone, and learn **where and how it is articulated**. Includes constructive exercises for rare phones.")
    with st.container(border=True):
        a, b, c = st.columns([2, 1.3, 1.3])
        with a:
            query = st.text_input("Search by symbol or description", placeholder="ɳ, retroflex, nasal, voiced …")
        with b:
            options = ["All categories", *CATEGORY_NAMES.values()]
            category = st.selectbox("Chart section", options)
        with c:
            selected_language = st.selectbox("Example language", ["All available", *LANGUAGES])
        d, e, f = st.columns(3)
        with d:
            places = sorted({sound.place for sound in SOUNDS.values() if sound.place})
            place = st.selectbox("Place of articulation", ["All places", *places])
        with e:
            manners = sorted({sound.manner for sound in SOUNDS.values() if sound.manner})
            manner = st.selectbox("Manner of articulation", ["All manners", *manners])
        with f:
            voicings = sorted({sound.voicing for sound in SOUNDS.values() if sound.voicing})
            voice = st.selectbox("Voicing", ["All voicing types", *voicings])

    match = []
    for sound in SOUNDS.values():
        if category != "All categories" and CATEGORY_NAMES[sound.category] != category:
            continue
        if place != "All places" and sound.place != place:
            continue
        if manner != "All manners" and sound.manner != manner:
            continue
        if voice != "All voicing types" and sound.voicing != voice:
            continue
        if query.casefold().strip() not in (sound.symbol + " " + sound.name + " " + sound.notes).casefold():
            continue
        match.append(sound)
    st.caption(f"{len(match)} sound(s) match your filters.")
    if match:
        default = next((i for i, sound in enumerate(match) if sound.symbol == "ɳ"), 0)
        phone = st.selectbox("Select a sound", match, index=default,
                             format_func=lambda item: f"{item.symbol} — {item.name}")
        display_description(phone.symbol, None if selected_language == "All available" else selected_language)
    else:
        st.warning("No matching sounds. Try removing one of your filters.")

    st.divider()
    st.markdown("#### Look up a combined IPA sequence")
    modified = st.text_input("Phone with diacritics or a tied affricate", value="t̪ʰ", help="Examples: t̪ʰ, d͡ʒ, aː, n̥")
    if modified.strip():
        display_description(modified.strip())


def analysis_page() -> None:
    st.title("IPA Transcription Analyser")
    st.write("Analyse **IPA notation already transcribed**. This is not speech recognition and does not infer IPA from ordinary spelling.")
    transcription = st.text_input("Paste an IPA transcription", value="[t̪ʰaːmiɻ]", max_chars=4000)
    if not transcription.strip():
        st.warning("Enter an IPA transcription to continue.")
        return
    try:
        result = tokenize(transcription)
    except ValueError as exc:
        st.error(str(exc))
        return
    m1, m2, m3 = st.columns(3)
    m1.metric("Phones recognised", result["sound_count"])
    m2.metric("Unknown characters", result["unknown_count"])
    m3.metric("Notation", result["notation"].capitalize())
    for warning in result.get("warnings", []):
        st.warning(warning)
    rows = []
    for token in result["tokens"]:
        detail = token.get("detail") or {}
        rows.append({
            "Symbol": token["text"], "Type": token["type"], "Name": detail.get("name", "—"),
            "Place": detail.get("place") or detail.get("backness") or "—",
            "Manner": detail.get("manner") or detail.get("height") or "—",
            "Voicing": detail.get("voicing") or "—",
            "Modifiers": ", ".join(item.get("name", "") for item in detail.get("modifiers", [])),
        })
    st.dataframe(rows, hide_index=True, use_container_width=True)
    sound_tokens = [t for t in result["tokens"] if t["type"] == "sound"]
    if sound_tokens:
        selected = st.selectbox("Explain a recognised phone", range(len(sound_tokens)),
                                format_func=lambda i: f"{sound_tokens[i]['text']} — {sound_tokens[i]['detail']['name']}")
        st.write(sound_tokens[selected]["detail"].get("description", ""))
    render_json(result, "ipa-transcription-analysis.json")


def comparison_page() -> None:
    st.title("Compare Phones")
    st.write("Compare two IPA phones in terms of place, manner, voicing and other articulatory properties.")
    a, b = st.columns(2)
    with a:
        first = st.text_input("Phone A", value="t", max_chars=15)
    with b:
        second = st.text_input("Phone B", value="ʈ", max_chars=15)
    if first and second:
        try:
            result = compare(first.strip(), second.strip())
        except ValueError as exc:
            st.error(str(exc))
            return
        a, b = st.columns(2)
        with a:
            st.markdown(f"### {result['a']['symbol']}")
            st.write(result["a"]["description"])
        with b:
            st.markdown(f"### {result['b']['symbol']}")
            st.write(result["b"]["description"])
        if result["contrasts"]:
            st.subheader("Feature differences")
            st.dataframe([{"Feature": label.replace("_", " ").capitalize(),
                           "Phone A": value["a"] if value["a"] is not None else "—",
                           "Phone B": value["b"] if value["b"] is not None else "—"}
                          for label, value in result["contrasts"].items()],
                         hide_index=True, use_container_width=True)
        else:
            st.info("The current descriptive feature fields do not distinguish these phones.")
        st.caption(result["note"])
        render_json(result, "ipa-sound-comparison.json")


def symbols_page() -> None:
    st.title("Diacritics, Stress and Tone")
    st.write("IPA modifiers and prosodic markers add phonetic detail beyond basic segment symbols.")
    tab1, tab2, tab3 = st.tabs(["Diacritics", "Stress and duration", "Tone notation"])
    for tab, rows in [(tab1, DIACRITIC_DATA), (tab2, SUPRA_DATA), (tab3, TONES)]:
        with tab:
            st.dataframe(list(rows.values()), hide_index=True, use_container_width=True)
            symbol = st.selectbox("Explain a symbol", list(rows.keys()), key=f"symbol-{id(rows)}",
                                  format_func=lambda s: f"{rows[s]['symbol']} — {rows[s]['name']}")
            st.info(rows[symbol].get("description", "See the IPA chart for interpretation."))
    st.caption("Pitch notation must be interpreted in the context of the relevant language and its analysis.")


def language_page() -> None:
    st.title("Examples by Language")
    st.write("Browse selected pedagogical examples. These are not exhaustive or verified phonetic dictionaries.")
    selected = st.selectbox("Language", LANGUAGES)
    if selected == "Marathi":
        rows = marathi_records()
        if not rows:
            st.warning("Marathi dataset missing: expected data/marathi_examples.csv.")
            return
        unique_words = len({row["orthography"] for row in rows})
        st.success(f"Loaded {len(rows)} source-derived pronunciation records for {unique_words} Marathi spellings.")
        st.caption("WikiPron/Wiktionary extractions, not independently speaker-verified. English glosses are editorial.")
        word_query = st.text_input("Search word, IPA or English meaning", key="marathi-word")
        col1, col2 = st.columns(2)
        with col1:
            level = st.selectbox("Transcription", ["Both", "broad", "narrow"], key="marathi-level")
        with col2:
            phones = sorted({tok for row in rows for tok in row["ipa_tokens"].split("|") if tok})
            phone = st.selectbox("IPA phone", ["All phones", *phones], key="marathi-phone")
        matches = [row for row in rows
                   if (not word_query or word_query.casefold() in
                       (row["orthography"] + " " + row["ipa"] + " " + row["meaning_en"]).casefold())
                   and (level == "Both" or row["transcription_level"] == level)
                   and (phone == "All phones" or phone in row["ipa_tokens"].split("|"))]
        st.caption(f"Showing {len(matches)} source-derived records")
        st.dataframe([{
            "Marathi": row["orthography"], "IPA": row["ipa"],
            "Type": row["transcription_level"],
            "English gloss (unverified)": row["meaning_en"],
            "Source": row["wiktionary_entry_url"]
        } for row in matches], hide_index=True, use_container_width=True)
        if matches:
            chosen = st.selectbox("Inspect source", list(dict.fromkeys(row["orthography"] for row in matches)))
            for row in [r for r in matches if r["orthography"] == chosen]:
                st.write(f"**{row['orthography']}** · `{row['ipa']}` · {row['transcription_level']}")
                st.caption(f"Original IPA segment sequence: {row['source_segmented_ipa']}")
                st.markdown(f"[Wiktionary entry]({row['wiktionary_entry_url']}) · [WikiPron source]({row['source_file_url']})")
        return
    matches = []
    for symbol, entries in EXAMPLES.items():
        for ex in entries:
            if ex.get("language", "").casefold() == selected.casefold():
                matches.append((symbol, ex))
    st.caption(f"{len(matches)} illustrative entries currently available for {selected}.")
    for symbol, example in matches:
        with st.container(border=True):
            st.markdown(f"### `{symbol}` · {example.get('word', '')}")
            st.write(f"**IPA:** `{example.get('ipa', '')}` · **Meaning:** {example.get('meaning') or '—'}")
            st.caption("Illustrative pronunciation only. Dialect-specific verification is recommended.")
    if not matches:
        st.warning("No curated examples currently exist for that language.")


def inventory_page() -> None:
    st.title("PHOIBLE Inventories")
    data = inventories_status()
    if not data.get("available"):
        st.info("PHOIBLE inventory data are optional and are **not included** in the downloadable code.")
        st.markdown("Download the dataset from [PHOIBLE](https://phoible.org/download), import it locally with `scripts/import_phoible.py`, and commit the generated database only if its licence and your repository's visibility permit. See `STREAMLIT_DEPLOY.md` for details.")
    else:
        st.success(f"Local PHOIBLE database available: {data.get('rows', 0)} phoneme records")
        language = st.text_input("Search language", value="Hindi")
        data = list_inventories(language=language.strip() or None, limit=100)
        items = data.get("items", [])
        if items:
            st.dataframe(items, hide_index=True, use_container_width=True)
            inventory = st.selectbox("Select an inventory", items,
                                     format_func=lambda row: f"{row['inventory_id']} — {row.get('language_name','')} — {row.get('dialect','')}")
            st.dataframe(inventory_items(str(inventory["inventory_id"]))["items"], hide_index=True, use_container_width=True)
        else:
            st.caption("No matching inventories. Try a different language or ISO code.")
        sym = st.text_input("Find inventory attestations of an IPA symbol", value="ɳ")
        if sym:
            st.dataframe(attestations(sym.strip(), language=language.strip() or None)["items"],
                         hide_index=True, use_container_width=True)
        st.warning("An attested phoneme in a published inventory is not evidence of a particular word's phonetic pronunciation.")


def english_page() -> None:
    st.title("English Pronunciation Dictionary")
    st.write("Optional US-English CMU Pronouncing Dictionary lookup with a broad ARPAbet-to-IPA approximation.")
    word = st.text_input("English word", value="phonetics")
    if not word.strip():
        return
    try:
        result = lookup_english(word.strip())
    except ValueError as exc:
        st.error(str(exc))
        return
    if not result["available"]:
        st.info("CMUdict is optional and not installed in this deployment. To enable it, add `cmudict>=1.0,<2` to `requirements.txt`, then redeploy; review its separate licence obligations first.")
    elif not result.get("found"):
        st.warning("Word not found in CMUdict.")
    else:
        for variant in result["variants"]:
            with st.container(border=True):
                st.markdown(f"### {variant['ipa_broad_no_stress_markers']}")
                st.write("ARPAbet:", " ".join(variant["arpabet"]))
                st.caption(variant["caveat"])
    render_json(result, "ipa-english-lookup.json")


pages = {
    "Explore sounds": explorer_page,
    "Analyse transcription": analysis_page,
    "Compare phones": comparison_page,
    "Diacritics and tone": symbols_page,
    "Language examples": language_page,
    "PHOIBLE inventories": inventory_page,
    "English dictionary": english_page,
}
with st.sidebar:
    st.title("🔤 IPA Atlas")
    st.caption("Interactive articulatory phonetics reference")
    page = st.radio("Navigation", list(pages), label_visibility="collapsed")
    st.divider()
    st.caption(f"{len(SOUNDS)} core and composite segment entries · {len(DIACRITIC_DATA)} diacritics")
    st.markdown(f"[IPA chart source]({SOURCE['url']})")
    st.caption("Reference descriptions are educational and are not substitutes for dialect-specific fieldwork.")

pages[page]()
st.divider()
st.caption("IPA Atlas · Educational phonetics toolkit. Core sound data are original explanations based on the IPA chart. Lexical examples require source/dialect verification. No third-party recordings are bundled.")
