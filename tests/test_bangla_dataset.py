"""Tests for sourced Bangla dialect-filtered pronunciation data."""
from ipa_atlas.bangla_lexicon import records, stats, search, examples_for_sound


def test_wikipron_file_coverage():
    s = stats()
    assert s["complete"] is True
    assert s["records"] == 28938
    assert s["unique_spellings"] > 6000
    assert {(r["dialect_filter"], r["transcription_level"]): r["count"]
            for r in s["by_source"]} == {
                ("Dhaka", "broad"): 7277,
                ("Dhaka", "narrow"): 6949,
                ("Rarh", "broad"): 7525,
                ("Rarh", "narrow"): 7187,
            }


def test_preserve_pronunciations_and_source_variation():
    entries = search(q="বাংলা")
    assert any(r["orthography"] == "বাংলা" and r["ipa"] == "/baŋla/"
               for r in entries)
    assert all(r["verification_status"] == "source_extracted_not_speaker_verified"
               for r in entries)
    words = search(q="বাড়ি", level="broad")
    assert any(r["dialect_filter"] == "Dhaka" and "ɹ" in r["ipa_tokens"] for r in words)
    assert any(r["dialect_filter"] == "Rarh" and "ɽ" in r["ipa_tokens"] for r in words)
    assert all(r["meaning_en"] == "" for r in words)


def test_exact_segment_matching_and_examples():
    aspirated = search(q="ছেলে", level="broad", phone="t͡ʃʰ")
    assert aspirated
    assert all("t͡ʃʰ" in r["ipa_tokens"] for r in aspirated)
    examples = examples_for_sound("ŋ", limit=8)
    assert examples
    assert len(examples) <= 8
    assert all(example["type"] == "source_derived_lexical_example"
               for example in examples)
    assert all(example["source_url"].startswith("https://en.wiktionary.org/wiki/")
               for example in examples)
