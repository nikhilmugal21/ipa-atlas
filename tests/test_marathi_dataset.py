import csv
from pathlib import Path
from ipa_atlas.marathi_lexicon import records,search,contains_phone,examples_for_sound

def test_dataset_is_loaded():
    rows=records()
    assert len(rows)>=180
    assert any(r['orthography']=='पाणी' and r['transcription_level']=='narrow' and r['ipa']=='[paɳiː]' for r in rows)
    assert all(r['source_file_url'].startswith('https://github.com/CUNY-CL/wikipron/') for r in rows)

def test_phone_lookup_and_variants():
    examples=examples_for_sound('ɳ','Marathi',limit=40)
    assert examples and any(e['word']=='पाणी' for e in examples)
    assert not examples_for_sound('ɳ','Tamil')
    r=search(q='पाणी')
    assert {x['transcription_level'] for x in r}=={'broad','narrow'}

def test_not_equating_aspiration():
    rows=search(q='खूप')
    assert rows and any(contains_phone(r,'kʰ') for r in rows)
    assert not any(contains_phone(r,'k') for r in rows)
