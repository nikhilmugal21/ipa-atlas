"""Source-audited Marathi lexical IPA add-on for IPA Atlas. Pure standard library."""
from __future__ import annotations
import csv
from functools import lru_cache
from pathlib import Path

DEFAULT_FILE=Path(__file__).resolve().parent.parent/'data'/'marathi_examples.csv'

@lru_cache(maxsize=8)
def _cached_records(path:str,mtime_ns:int):
    with open(path,encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def records(path:Path|str=DEFAULT_FILE):
    p=Path(path)
    return _cached_records(str(p.resolve()),p.stat().st_mtime_ns) if p.is_file() else []

def tokens(entry:dict):
    return entry.get('ipa_tokens','').split('|')

def _base(token:str):
    # Match a chart-base symbol to its phonetic modifications without
    # erasing other phonemic contrasts (notably aspiration, ʰ, or length, ː).
    import unicodedata
    return ''.join(ch for ch in token if not unicodedata.combining(ch) and ch not in '̪̆')

def contains_phone(entry:dict,phone:str,allow_modified:bool=True)->bool:
    if not phone:return True
    phonemes=tokens(entry)
    if phone in phonemes:return True
    if allow_modified:
        return any(_base(tok)==phone for tok in phonemes)
    return False

def search(q:str='',phone:str='',level:str='',limit:int=300,path:Path|str=DEFAULT_FILE):
    items=records(path)
    if q:
        items=[r for r in items if q.casefold() in (r['orthography']+' '+r['meaning_en']+' '+r['ipa']).casefold()]
    if phone:items=[r for r in items if contains_phone(r,phone)]
    if level:items=[r for r in items if r['transcription_level']==level]
    return items[:max(0,min(limit,5000))]

def examples_for_sound(phone:str,language:str|None=None,limit:int=8,path:Path|str=DEFAULT_FILE):
    if language and language.casefold()!='marathi':return []
    rows=search(phone=phone,limit=5000,path=path)
    # Prefer broad illustrative items and then narrow; don't suppress an alternate source entry.
    rows.sort(key=lambda r:(r['transcription_level']!='broad',len(r['orthography']),r['orthography']))
    return [{
      'language':'Marathi','word':r['orthography'],'ipa':r['ipa'],
      'meaning':r['meaning_en'] or None,'type':'source_attested_lexical_example',
      'verification':'WikiPron source-extracted; not expert-reviewed',
      'notes':f"{r['transcription_level']} transcription; dialect not established; meaning editorial/unverified",
      'source_url':r['wiktionary_entry_url'],'source_file_url':r['source_file_url'],
      'dataset_id':r['id'],
    } for r in rows[:limit]]
