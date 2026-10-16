"""Read-only, optional, PHOIBLE-style imported SQLite inventories.

A recorded PHOIBLE phoneme is *not* a claim about a realised phone in a word.
"""
from __future__ import annotations
from pathlib import Path
import os,sqlite3
DEFAULT_PATH=Path(__file__).resolve().parent.parent/'data'/'phoible.sqlite'

def db_path():return Path(os.environ.get('IPA_ATLAS_PHOIBLE_DB',str(DEFAULT_PATH)))

def status():
 path=db_path()
 if not path.is_file():return {"available":False,"message":"Download PHOIBLE CSV from https://phoible.org/download, then run scripts/import_phoible.py. No PHOIBLE data is bundled."}
 try:
  with sqlite3.connect(f'file:{path}?mode=ro',uri=True) as conn:
   count=conn.execute('select count(*) from phonemes').fetchone()[0]
  return {"available":True,"rows":count,"db_location":"local server data"}
 except sqlite3.Error:
  return {"available":False,"message":"Inventory DB exists but does not match the importer schema."}

def list_inventories(language:str|None=None,iso6393:str|None=None,limit:int=30):
 if not status()['available']:return {**status(),"items":[]}
 clauses=[];args=[]
 if language:clauses.append('language_name LIKE ?');args.append('%'+language+'%')
 if iso6393:clauses.append('iso6393 = ?');args.append(iso6393)
 where='where '+' and '.join(clauses) if clauses else ''
 with sqlite3.connect(f'file:{db_path()}?mode=ro',uri=True) as conn:
  conn.row_factory=sqlite3.Row
  rows=conn.execute(f'''select inventory_id,language_name,iso6393,glottocode,dialect,COUNT(*) AS segment_count,
                 SUM(CASE WHEN segment_class='consonant' THEN 1 ELSE 0 END) AS consonant_count,
                 SUM(CASE WHEN segment_class='vowel' THEN 1 ELSE 0 END) AS vowel_count
                 from phonemes {where} group by inventory_id,language_name,iso6393,glottocode,dialect order by language_name,inventory_id limit ?''',[*args,limit]).fetchall()
 return {'available':True,'source':'PHOIBLE imported locally, source inventory IDs preserved','note':'Different inventories can describe different doculects or sources; never merge without stating this.', 'items':[dict(r) for r in rows]}

def inventory_items(inventory_id:str):
 if not status()['available']:return {**status(),"items":[]}
 with sqlite3.connect(f'file:{db_path()}?mode=ro',uri=True) as conn:
  conn.row_factory=sqlite3.Row
  rows=conn.execute('select phoneme,segment_class,marginal,source,language_name,iso6393,dialect from phonemes where inventory_id=? order by segment_class,phoneme limit 400',[inventory_id]).fetchall()
 return {'available':True,'inventory_id':inventory_id,'items':[dict(r) for r in rows],'note':'PHOIBLE inventory phonemes are contrastive units in cited doculect analyses, NOT isolated phone recordings or pronunciation examples.'}

def attestations(symbol:str,language:str|None=None,limit:int=50):
 if not status()['available']:return {**status(),"items":[]}
 where='phoneme=?';args=[symbol]
 if language:where+=' and (language_name like ? or iso6393=?)';args.extend(['%'+language+'%',language])
 with sqlite3.connect(f'file:{db_path()}?mode=ro',uri=True) as conn:
  conn.row_factory=sqlite3.Row
  rows=conn.execute(f'select distinct inventory_id,language_name,iso6393,dialect,segment_class,source from phonemes where {where} limit ?',[*args,limit]).fetchall()
 return {'available':True,'symbol':symbol,'items':[dict(r) for r in rows],'note':'Presence in PHOIBLE refers to a reported phoneme in a documented inventory and does NOT prove a phonetic pronunciation in a word.'}
