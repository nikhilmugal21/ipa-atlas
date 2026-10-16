"""Read-only Bangla (Bengali) pronunciation examples from WikiPron/Wiktionary.

Data were extracted by WikiPron from Wiktionary; they are NOT independent
acoustic evidence, nor guaranteed to reflect every speaker of a dialect.
The dialect-selected files may include entries without an explicit dialect tag.
Do not infer word meanings, stress, or phonemic analyses from orthography.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "bangla_wikipron"

# Filename + immutable original Git blob identifier, captured 2026-10-16.
SOURCE_FILES = {
    ("Dhaka", "broad"): ("ben_beng_dhaka_broad.tsv", "6ab23861f695e9172ae09881265b3523267a8aa5"),
    ("Dhaka", "narrow"): ("ben_beng_dhaka_narrow.tsv", "e3eb58cc0b2cc3a1acd9ad4f5acc7b6ac352579c"),
    ("Rarh", "broad"): ("ben_beng_rarh_broad.tsv", "53e2dc72b043d2c6960813352587944def88d56a"),
    ("Rarh", "narrow"): ("ben_beng_rarh_narrow.tsv", "37baeb445c7f0bbb59d6a423283171abda706783"),
}

SOURCE_BASE = "https://github.com/CUNY-CL/wikipron/blob/master/data/scrape/tsv/"


@lru_cache(maxsize=1)
def records() -> tuple[dict, ...]:
    """Load all source rows; retain repeated spellings and variant pronunciations."""
    output = []
    for (dialect, level), (filename, sha) in SOURCE_FILES.items():
        path = DATA_DIR / filename
        if not path.is_file():
            continue
        with path.open("r", encoding="utf-8-sig") as f:
            for line_no, line in enumerate(f, start=1):
                if "\t" not in line:
                    continue
                word, segmented = line.rstrip("\r\n").split("\t", 1)
                word, segmented = word.strip(), segmented.strip()
                tokens = segmented.split()
                if not word or not tokens:
                    continue
                output.append({
                    "id": f"ben-{dialect.lower()}-{level}-{line_no}",
                    "language": "Bangla", "iso6393": "ben",
                    "orthography": word,
                    "ipa": ("/" if level == "broad" else "[") + "".join(tokens) + ("/" if level == "broad" else "]"),
                    "ipa_tokens": tokens,
                    "source_segmented_ipa": segmented,
                    "transcription_level": level,
                    "dialect_filter": dialect,
                    "dialect_caveat": "WikiPron dialect filter; unlabeled Wiktionary entries may also be included.",
                    "source_name": "WikiPron / Wiktionary",
                    "source_file": filename,
                    "source_blob_sha": sha,
                    "source_file_url": SOURCE_BASE + filename,
                    "wiktionary_entry_url": "https://en.wiktionary.org/wiki/" + quote(word, safe=""),
                    "verification_status": "source_extracted_not_speaker_verified",
                    "meaning_en": "",
                })
    return tuple(output)


def stats() -> dict:
    rows = records()
    counts = Counter((row["dialect_filter"], row["transcription_level"]) for row in rows)
    return {
        "records": len(rows),
        "unique_spellings": len({row["orthography"] for row in rows}),
        "by_source": [
            {"dialect_filter": d, "transcription_level": l, "count": counts[(d, l)]}
            for d in ("Dhaka", "Rarh") for l in ("broad", "narrow")
        ],
        "complete": all((DATA_DIR / spec[0]).is_file() for spec in SOURCE_FILES.values()),
        "warning": "WikiPron-mined Wiktionary data, not independently verified recordings; dialect-filtered files may include unlabeled entries.",
    }


def search(
    q: str = "", dialect: str | None = None,
    level: str | None = None, phone: str | None = None
) -> list[dict]:
    """Exact IPA-token lookup (not substring lookup), with optional lexical filters."""
    query = q.strip().casefold()
    return [
        row for row in records()
        if (not query or query in (row["orthography"] + " " + row["ipa"]).casefold())
        and (not dialect or row["dialect_filter"] == dialect)
        and (not level or row["transcription_level"] == level)
        and (not phone or phone in row["ipa_tokens"])
    ]


def examples_for_sound(phone: str, limit: int = 8) -> list[dict]:
    """Choose source examples balanced across the two dialect-filter groups."""
    limit = max(0, min(limit, 30))
    candidate = search(level="broad", phone=phone)
    groups = {
        dialect: sorted(
            (r for r in candidate if r["dialect_filter"] == dialect),
            key=lambda x: (len(x["orthography"]), x["orthography"], x["ipa"]),
        )
        for dialect in ("Dhaka", "Rarh")
    }
    picked: list[dict] = []
    used: set[tuple[str, str, str]] = set()
    for rank in range(max(len(items) for items in groups.values()) if groups else 0):
        for dialect in ("Dhaka", "Rarh"):
            rows = groups[dialect]
            if rank >= len(rows):
                continue
            row = rows[rank]
            key = row["orthography"], row["ipa"], row["dialect_filter"]
            if key in used:
                continue
            used.add(key)
            picked.append({
                "language": "Bangla", "word": row["orthography"],
                "ipa": row["ipa"], "meaning": None,
                "type": "source_derived_lexical_example",
                "verification": row["verification_status"],
                "notes": f"{row['dialect_filter']} filter · {row['transcription_level']} · meaning not supplied",
                "source_url": row["wiktionary_entry_url"],
            })
            if len(picked) >= limit:
                return picked
    return picked
